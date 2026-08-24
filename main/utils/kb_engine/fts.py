"""Transactional SQLite FTS5 and vector index over Evidence Passages."""

from __future__ import annotations

import json
import os
import re
import sqlite3
import tempfile
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal

import sqlite_vec  # type: ignore[import-untyped]

from .chunker import StructureAwareChunker
from .embedder import PassageEmbedder
from .errors import (
    CorpusChangedDuringSyncError,
    EmptyCorpusError,
    IndexNotBuiltError,
    InvalidIndexError,
    InvalidIndexPathError,
    InvalidKnowledgeSourceError,
    InvalidSearchError,
    StaleIndexError,
)
from .models import (
    CorpusManifest,
    EvidencePassage,
    EvidenceSearchResult,
    IndexBuildMetrics,
    IndexState,
    IndexStatus,
    PassageSizeStatus,
)
from .query_preprocessor import preprocess_query
from .sync import build_corpus_manifest

_SCHEMA_VERSION = "4"
_VALID_SOURCE_TYPES = frozenset({"article", "podcast"})
_VALID_SIZE_STATUSES = frozenset(status.value for status in PassageSizeStatus)
_PASSAGE_COLUMNS = """
    p.chunk_id AS chunk_id,
    s.slug AS source_slug,
    s.rel_path AS rel_path,
    s.title AS title,
    s.author AS author,
    s.language AS language,
    s.source_type AS source_type,
    s.category AS category,
    s.topics AS topics,
    s.source AS source,
    p.section_hierarchy AS section_hierarchy,
    p.start_line AS start_line,
    p.end_line AS end_line,
    p.content AS content,
    p.word_count AS word_count,
    p.char_count AS char_count,
    p.citation AS citation,
    p.size_status AS size_status
"""


@dataclass(frozen=True, slots=True)
class _IndexSnapshot:
    metadata: dict[str, str]
    passage_count: int


@dataclass(frozen=True, slots=True)
class _DatabaseBuildResult:
    passage_count: int
    metrics: IndexBuildMetrics


@dataclass(frozen=True, slots=True)
class _SourceReuseResult:
    passage_count: int
    vector_insertion_seconds: float


class PassageIndex:
    """Own the local Derived Index and enforce explicit synchronization."""

    def __init__(
        self,
        kb_dir: Path,
        db_path: Path,
        chunker: StructureAwareChunker | None = None,
    ) -> None:
        self.kb_dir = kb_dir.resolve()
        configured_db_path = db_path.expanduser()
        if configured_db_path.is_symlink():
            raise InvalidIndexPathError(
                configured_db_path, "symbolic links are not allowed"
            )
        self.db_path = configured_db_path.resolve()
        if self.db_path.suffix.casefold() not in {".sqlite", ".sqlite3", ".db"}:
            raise InvalidIndexPathError(
                self.db_path, "use a .sqlite, .sqlite3, or .db file"
            )
        if self.db_path == self.kb_dir or self.kb_dir in self.db_path.parents:
            raise InvalidIndexPathError(
                self.db_path, "the index must be stored outside Knowledge_base"
            )
        if self.db_path.is_dir():
            raise InvalidIndexPathError(self.db_path, "the path is a directory")
        self.chunker = chunker or StructureAwareChunker(self.kb_dir)
        self.last_build_metrics: IndexBuildMetrics | None = None

    def synchronize(self) -> IndexStatus:
        synchronization_started = time.perf_counter()
        self.last_build_metrics = None
        manifest_started = time.perf_counter()
        manifest = build_corpus_manifest(self.kb_dir)
        manifest_seconds = time.perf_counter() - manifest_started
        if manifest.document_count == 0:
            raise EmptyCorpusError
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{self.db_path.name}.",
                suffix=".tmp",
                dir=self.db_path.parent,
            )
        except OSError as error:
            raise InvalidIndexPathError(
                self.db_path, f"the parent directory is not writable: {error}"
            ) from error
        os.close(descriptor)
        temporary_path = Path(temporary_name)

        try:
            build_result = self._build_database(temporary_path, manifest)
            verification_started = time.perf_counter()
            verification_manifest = build_corpus_manifest(self.kb_dir)
            manifest_seconds += time.perf_counter() - verification_started
            if verification_manifest.digest != manifest.digest:
                raise CorpusChangedDuringSyncError
            replacement_started = time.perf_counter()
            os.replace(temporary_path, self.db_path)
            replacement_seconds = time.perf_counter() - replacement_started
        except sqlite3.DatabaseError as error:
            raise InvalidIndexError from error
        except OSError as error:
            raise InvalidIndexPathError(
                self.db_path, f"the index could not be replaced: {error}"
            ) from error
        finally:
            temporary_path.unlink(missing_ok=True)

        self.last_build_metrics = replace(
            build_result.metrics,
            total_seconds=time.perf_counter() - synchronization_started,
            manifest_seconds=manifest_seconds,
            replacement_seconds=replacement_seconds,
        )
        return IndexStatus(
            state=IndexState.FRESH,
            document_count=manifest.document_count,
            passage_count=build_result.passage_count,
            current_digest=manifest.digest,
            indexed_digest=manifest.digest,
        )

    def status(self) -> IndexStatus:
        manifest = build_corpus_manifest(self.kb_dir)
        if not self.db_path.is_file():
            return IndexStatus(
                state=IndexState.MISSING,
                document_count=manifest.document_count,
                passage_count=0,
                current_digest=manifest.digest,
                indexed_digest=None,
            )

        try:
            with self._connect() as connection:
                snapshot = self._inspect_database(connection)
        except (sqlite3.DatabaseError, TypeError, ValueError):
            return IndexStatus(
                state=IndexState.INVALID,
                document_count=manifest.document_count,
                passage_count=0,
                current_digest=manifest.digest,
                indexed_digest=None,
            )

        indexed_digest = snapshot.metadata.get("corpus_digest")
        if (
            snapshot.metadata.get("schema_version") != _SCHEMA_VERSION
            or snapshot.metadata.get("embedding_model") != PassageEmbedder.model_name()
            or not indexed_digest
        ):
            state = IndexState.INVALID
        elif indexed_digest == manifest.digest:
            state = IndexState.FRESH
        else:
            state = IndexState.STALE
        return IndexStatus(
            state=state,
            document_count=manifest.document_count,
            passage_count=snapshot.passage_count,
            current_digest=manifest.digest,
            indexed_digest=indexed_digest,
        )

    def search(
        self,
        query: str,
        category: str | None = None,
        topic: str | None = None,
        source_slug: str | None = None,
        limit: int = 20,
        mode: Literal["hybrid", "bm25", "dense"] = "hybrid",
        retain_evidence: bool = True,
    ) -> tuple[EvidenceSearchResult, ...]:
        """Search the Knowledge Base using hybrid, BM25, or dense retrieval."""
        if not 1 <= limit <= 50:
            raise InvalidSearchError("limit must be between 1 and 50")
        tokens = [token for token in re.findall(r"\w+", query) if len(token) > 1]
        if not tokens:
            raise InvalidSearchError("query must contain at least one searchable term")

        if mode == "bm25":
            return self.search_bm25(
                query=query,
                category=category,
                topic=topic,
                source_slug=source_slug,
                limit=limit,
            )
        elif mode == "dense":
            return self.search_dense(
                query=query,
                category=category,
                topic=topic,
                source_slug=source_slug,
                limit=limit,
            )
        elif mode == "hybrid":
            from .hybrid import search_hybrid

            return search_hybrid(
                index=self,
                query=query,
                category=category,
                topic=topic,
                source_slug=source_slug,
                limit=limit,
                retain_evidence=retain_evidence,
            )
        else:
            raise InvalidSearchError(f"unknown search mode: {mode}")

    def search_bm25(
        self,
        query: str,
        category: str | None = None,
        topic: str | None = None,
        source_slug: str | None = None,
        limit: int = 5,
    ) -> tuple[EvidenceSearchResult, ...]:
        """Search passages using sparse lexical SQLite FTS5 BM25 retrieval."""
        if not 1 <= limit <= 50:
            raise InvalidSearchError("limit must be between 1 and 50")
        tokens = [token for token in re.findall(r"\w+", query) if len(token) > 1]
        if not tokens:
            raise InvalidSearchError("query must contain at least one searchable term")
        self._require_fresh_index()
        fts_query = preprocess_query(query)

        sql = f"""
            SELECT {_PASSAGE_COLUMNS},
                   bm25(passages_fts, 5.0, 1.0, 2.0, 4.0, 2.0, 1.0)
                       AS lexical_rank
            FROM passages_fts
            JOIN passages p ON p.id = passages_fts.rowid
            JOIN sources s ON s.id = p.source_id
            WHERE passages_fts MATCH ?
        """
        parameters: list[object] = [fts_query]
        if category:
            sql += " AND s.category = ?"
            parameters.append(category)
        if topic:
            sql += " AND EXISTS (SELECT 1 FROM json_each(s.topics) WHERE value = ?)"
            parameters.append(topic)
        if source_slug:
            sql += " AND s.slug = ?"
            parameters.append(source_slug)
        sql += " ORDER BY rank, p.chunk_id LIMIT ?"
        parameters.append(limit)

        try:
            with self._connect() as connection:
                rows = connection.execute(sql, parameters).fetchall()
            return tuple(
                EvidenceSearchResult(
                    passage=self._passage_from_row(row),
                    lexical_score=round(-float(row["lexical_rank"]), 8),
                )
                for row in rows
            )
        except (sqlite3.DatabaseError, TypeError, ValueError) as error:
            raise InvalidIndexError from error

    def search_dense(
        self,
        query: str,
        category: str | None = None,
        topic: str | None = None,
        source_slug: str | None = None,
        limit: int = 20,
    ) -> tuple[EvidenceSearchResult, ...]:
        """Search passages using neural dense vector embeddings (bge-small-en-v1.5)."""
        if not 1 <= limit <= 50:
            raise InvalidSearchError("limit must be between 1 and 50")
        tokens = [token for token in re.findall(r"\w+", query) if len(token) > 1]
        if not tokens:
            raise InvalidSearchError("query must contain at least one searchable term")
        self._require_fresh_index()
        query_bytes = PassageEmbedder.embed_query_to_bytes(query)

        vec_k = max(limit * 3, 50)
        sql = f"""
            SELECT {_PASSAGE_COLUMNS}, v.distance AS cosine_distance
            FROM vec_passages v
            JOIN passages p ON p.id = v.passage_id
            JOIN sources s ON s.id = p.source_id
            WHERE v.embedding MATCH ? AND k = ?
        """
        parameters: list[object] = [query_bytes, vec_k]
        if category:
            sql += " AND s.category = ?"
            parameters.append(category)
        if topic:
            sql += " AND EXISTS (SELECT 1 FROM json_each(s.topics) WHERE value = ?)"
            parameters.append(topic)
        if source_slug:
            sql += " AND s.slug = ?"
            parameters.append(source_slug)
        sql += " ORDER BY v.distance ASC, p.chunk_id LIMIT ?"
        parameters.append(limit)

        try:
            with self._connect() as connection:
                rows = connection.execute(sql, parameters).fetchall()
            return tuple(
                EvidenceSearchResult(
                    passage=self._passage_from_row(row),
                    lexical_score=0.0,
                    dense_score=round(1.0 - float(row["cosine_distance"]), 8),
                )
                for row in rows
            )
        except (sqlite3.DatabaseError, TypeError, ValueError) as error:
            raise InvalidIndexError from error

    def get_passage(self, chunk_id: str) -> EvidencePassage | None:
        self._require_fresh_index()
        try:
            with self._connect() as connection:
                row = connection.execute(
                    f"""
                        SELECT {_PASSAGE_COLUMNS}
                        FROM passages p
                        JOIN sources s ON s.id = p.source_id
                        WHERE p.chunk_id = ?
                    """,
                    (chunk_id,),
                ).fetchone()
            return self._passage_from_row(row) if row else None
        except (sqlite3.DatabaseError, TypeError, ValueError) as error:
            raise InvalidIndexError from error

    def _build_database(
        self, path: Path, manifest: CorpusManifest
    ) -> _DatabaseBuildResult:
        previous_connection = self._open_reusable_index()
        sqlite_fts_started = time.perf_counter()
        chunking_seconds = 0.0
        model_initialization_seconds = 0.0
        embedding_seconds = 0.0
        vector_insertion_seconds = 0.0
        validation_seconds = 0.0
        reused_source_count = 0
        rebuilt_source_count = 0
        reused_passage_count = 0
        passage_count = 0
        passage_entries: list[tuple[int, str]] = []

        try:
            with sqlite3.connect(path) as connection:
                self._load_sqlite_vec(connection)
                connection.row_factory = sqlite3.Row
                connection.execute("PRAGMA foreign_keys = ON")
                self._create_schema(connection)

                for rel_path, source_digest in manifest.source_digests:
                    reuse_result = self._reuse_source(
                        connection,
                        previous_connection,
                        rel_path,
                        source_digest,
                    )
                    if reuse_result is not None:
                        reused_source_count += 1
                        reused_passage_count += reuse_result.passage_count
                        passage_count += reuse_result.passage_count
                        vector_insertion_seconds += (
                            reuse_result.vector_insertion_seconds
                        )
                        continue

                    rebuilt_source_count += 1
                    source_path = self.kb_dir / rel_path
                    chunking_started = time.perf_counter()
                    passages = self.chunker.chunk_document(
                        source_path,
                        expected_digest=source_digest,
                    )
                    chunking_seconds += time.perf_counter() - chunking_started
                    if not passages:
                        raise InvalidKnowledgeSourceError(
                            rel_path,
                            "chunking produced no Evidence Passages",
                        )
                    source_id = self._insert_source(
                        connection, passages[0], source_digest
                    )
                    for passage in passages:
                        passage_count += 1
                        passage_id = self._insert_passage(
                            connection, source_id, passage
                        )
                        passage_text = (
                            f"{passage.title}\n"
                            f"{passage.section_path}\n"
                            f"{passage.content}"
                        )
                        passage_entries.append((passage_id, passage_text))

                if passage_entries:
                    passage_ids, texts = zip(*passage_entries, strict=True)
                    model_initialization_started = time.perf_counter()
                    PassageEmbedder.get_model()
                    model_initialization_seconds = (
                        time.perf_counter() - model_initialization_started
                    )
                    embedding_started = time.perf_counter()
                    embedding_bytes = PassageEmbedder.embed_texts_to_bytes(
                        list(texts), batch_size=128
                    )
                    embedding_seconds = time.perf_counter() - embedding_started
                    vector_insertion_started = time.perf_counter()
                    connection.executemany(
                        "INSERT INTO vec_passages (passage_id, embedding) "
                        "VALUES (?, ?)",
                        list(zip(passage_ids, embedding_bytes, strict=True)),
                    )
                    vector_insertion_seconds += (
                        time.perf_counter() - vector_insertion_started
                    )

                metadata = {
                    "schema_version": _SCHEMA_VERSION,
                    "embedding_model": PassageEmbedder.model_name(),
                    "corpus_digest": manifest.digest,
                    "document_count": str(manifest.document_count),
                    "passage_count": str(passage_count),
                }
                connection.executemany(
                    "INSERT INTO meta (key, value) VALUES (?, ?)", metadata.items()
                )
                connection.commit()
                validation_started = time.perf_counter()
                snapshot = self._inspect_database(connection)
                validation_seconds = time.perf_counter() - validation_started
        finally:
            if previous_connection is not None:
                previous_connection.close()

        sqlite_fts_total = time.perf_counter() - sqlite_fts_started
        sqlite_fts_seconds = max(
            0.0,
            sqlite_fts_total
            - chunking_seconds
            - model_initialization_seconds
            - embedding_seconds
            - vector_insertion_seconds
            - validation_seconds,
        )
        return _DatabaseBuildResult(
            passage_count=snapshot.passage_count,
            metrics=IndexBuildMetrics(
                total_seconds=0.0,
                manifest_seconds=0.0,
                sqlite_fts_seconds=sqlite_fts_seconds,
                chunking_seconds=chunking_seconds,
                model_initialization_seconds=model_initialization_seconds,
                embedding_seconds=embedding_seconds,
                vector_insertion_seconds=vector_insertion_seconds,
                validation_seconds=validation_seconds,
                replacement_seconds=0.0,
                reused_source_count=reused_source_count,
                rebuilt_source_count=rebuilt_source_count,
                reused_passage_count=reused_passage_count,
                embedded_passage_count=len(passage_entries),
            ),
        )

    def _open_reusable_index(self) -> sqlite3.Connection | None:
        if not self.db_path.is_file():
            return None
        connection: sqlite3.Connection | None = None
        try:
            connection = sqlite3.connect(
                f"{self.db_path.as_uri()}?mode=ro",
                uri=True,
            )
            self._load_sqlite_vec(connection)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA query_only = ON")
            snapshot = self._inspect_database(connection)
            if (
                snapshot.metadata.get("schema_version") != _SCHEMA_VERSION
                or snapshot.metadata.get("embedding_model")
                != PassageEmbedder.model_name()
            ):
                connection.close()
                return None
            return connection
        except (OSError, sqlite3.DatabaseError, TypeError, ValueError):
            if connection is not None:
                connection.close()
            return None

    def _reuse_source(
        self,
        connection: sqlite3.Connection,
        previous_connection: sqlite3.Connection | None,
        rel_path: str,
        source_digest: str,
    ) -> _SourceReuseResult | None:
        if previous_connection is None:
            return None
        rows = previous_connection.execute(
            f"""
                SELECT {_PASSAGE_COLUMNS}, v.embedding AS embedding
                FROM passages p
                JOIN sources s ON s.id = p.source_id
                JOIN vec_passages v ON v.passage_id = p.id
                WHERE s.rel_path = ? AND s.content_digest = ?
                ORDER BY p.id
            """,
            (rel_path, source_digest),
        ).fetchall()
        if not rows:
            return None

        first_passage = self._rebase_reused_citation(
            self._passage_from_row(rows[0]), rel_path
        )
        source_id = self._insert_source(connection, first_passage, source_digest)
        vector_insertion_seconds = 0.0
        for row in rows:
            passage = self._rebase_reused_citation(
                self._passage_from_row(row), rel_path
            )
            passage_id = self._insert_passage(
                connection,
                source_id,
                passage,
            )
            embedding = row["embedding"]
            if not isinstance(embedding, bytes):
                raise sqlite3.DatabaseError("stored embedding is not binary")
            vector_insertion_started = time.perf_counter()
            connection.execute(
                "INSERT INTO vec_passages (passage_id, embedding) VALUES (?, ?)",
                (passage_id, embedding),
            )
            vector_insertion_seconds += time.perf_counter() - vector_insertion_started
        return _SourceReuseResult(
            passage_count=len(rows),
            vector_insertion_seconds=vector_insertion_seconds,
        )

    def _rebase_reused_citation(
        self, passage: EvidencePassage, rel_path: str
    ) -> EvidencePassage:
        source_uri = (self.kb_dir / rel_path).as_uri()
        citation = f"{source_uri}#L{passage.start_line}-L{passage.end_line}"
        return replace(passage, citation=citation)

    @staticmethod
    def _load_sqlite_vec(connection: sqlite3.Connection) -> None:
        connection.enable_load_extension(True)
        sqlite_vec.load(connection)
        connection.enable_load_extension(False)

    @classmethod
    def _create_schema(cls, connection: sqlite3.Connection) -> None:
        connection.executescript(
            """
            CREATE TABLE meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE sources (
                id INTEGER PRIMARY KEY,
                slug TEXT NOT NULL UNIQUE,
                rel_path TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                language TEXT NOT NULL CHECK (language = 'en'),
                source_type TEXT NOT NULL,
                category TEXT NOT NULL,
                topics TEXT NOT NULL,
                source TEXT NOT NULL,
                content_digest TEXT NOT NULL
                    CHECK (length(content_digest) = 64)
            );

            CREATE TABLE passages (
                id INTEGER PRIMARY KEY,
                chunk_id TEXT NOT NULL UNIQUE,
                source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
                section_hierarchy TEXT NOT NULL,
                start_line INTEGER NOT NULL CHECK (start_line >= 1),
                end_line INTEGER NOT NULL CHECK (end_line >= start_line),
                content TEXT NOT NULL,
                word_count INTEGER NOT NULL,
                char_count INTEGER NOT NULL,
                citation TEXT NOT NULL,
                size_status TEXT NOT NULL
            );

            CREATE VIRTUAL TABLE passages_fts USING fts5(
                title,
                author,
                category,
                topics,
                section_path,
                content
            );

            CREATE VIRTUAL TABLE vec_passages USING vec0(
                passage_id INTEGER PRIMARY KEY,
                embedding float[384] distance_metric=cosine
            );

            CREATE INDEX passages_source_id ON passages(source_id);
            """
        )

    @staticmethod
    def _insert_source(
        connection: sqlite3.Connection,
        passage: EvidencePassage,
        content_digest: str,
    ) -> int:
        cursor = connection.execute(
            """
                INSERT INTO sources (
                    slug, rel_path, title, author, language,
                    source_type, category, topics, source, content_digest
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                passage.source_slug,
                passage.rel_path,
                passage.title,
                passage.author,
                passage.language,
                passage.source_type,
                passage.category,
                json.dumps(passage.topics, ensure_ascii=False),
                passage.source,
                content_digest,
            ),
        )
        return _last_row_id(cursor)

    @staticmethod
    def _insert_passage(
        connection: sqlite3.Connection,
        source_id: int,
        passage: EvidencePassage,
    ) -> int:
        cursor = connection.execute(
            """
                INSERT INTO passages (
                    chunk_id, source_id, section_hierarchy, start_line,
                    end_line, content, word_count, char_count, citation, size_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                passage.chunk_id,
                source_id,
                json.dumps(passage.section_hierarchy, ensure_ascii=False),
                passage.start_line,
                passage.end_line,
                passage.content,
                passage.word_count,
                passage.char_count,
                passage.citation,
                passage.size_status.value,
            ),
        )
        row_id = _last_row_id(cursor)
        connection.execute(
            """
                INSERT INTO passages_fts (
                    rowid, title, author, category, topics, section_path, content
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row_id,
                passage.title,
                passage.author,
                passage.category,
                " ".join(passage.topics),
                passage.section_path,
                passage.content,
            ),
        )
        return row_id

    @classmethod
    def _inspect_database(cls, connection: sqlite3.Connection) -> _IndexSnapshot:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()
        if not integrity or integrity[0] != "ok":
            raise sqlite3.DatabaseError("SQLite integrity check failed")
        if connection.execute("PRAGMA foreign_key_check").fetchone():
            raise sqlite3.DatabaseError("SQLite foreign-key check failed")

        metadata = {
            str(row[0]): str(row[1])
            for row in connection.execute("SELECT key, value FROM meta")
        }
        source_count = _table_count(connection, "sources")
        passage_count = _table_count(connection, "passages")
        fts_count = _table_count(connection, "passages_fts")
        vec_count = _table_count(connection, "vec_passages")

        try:
            expected_sources = int(metadata["document_count"])
            expected_passages = int(metadata["passage_count"])
        except (KeyError, ValueError) as error:
            raise sqlite3.DatabaseError("index metadata is incomplete") from error
        if source_count != expected_sources:
            raise sqlite3.DatabaseError("source count does not match index metadata")
        if (
            passage_count != expected_passages
            or fts_count != passage_count
            or vec_count != passage_count
        ):
            raise sqlite3.DatabaseError("passage tables have inconsistent counts")
        missing_fts_rows = connection.execute(
            """
            SELECT COUNT(*)
            FROM passages p
            LEFT JOIN passages_fts f ON f.rowid = p.id
            WHERE f.rowid IS NULL
            """
        ).fetchone()
        if not missing_fts_rows or int(missing_fts_rows[0]):
            raise sqlite3.DatabaseError("passage search rows are incomplete")

        _validate_source_rows(connection)
        _validate_passage_rows(connection)
        _validate_fts_rows(connection)

        return _IndexSnapshot(
            metadata=metadata,
            passage_count=passage_count,
        )

    def _require_fresh_index(self) -> None:
        state = self.status().state
        if state is IndexState.MISSING:
            raise IndexNotBuiltError
        if state is IndexState.STALE:
            raise StaleIndexError
        if state is IndexState.INVALID:
            raise InvalidIndexError

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        self._load_sqlite_vec(connection)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @staticmethod
    def _passage_from_row(row: sqlite3.Row) -> EvidencePassage:
        return EvidencePassage(
            chunk_id=str(row["chunk_id"]),
            source_slug=str(row["source_slug"]),
            rel_path=str(row["rel_path"]),
            title=str(row["title"]),
            author=str(row["author"]),
            language=str(row["language"]),
            source_type=str(row["source_type"]),
            category=str(row["category"]),
            topics=_decode_string_array(row["topics"], "topics"),
            source=str(row["source"]),
            section_hierarchy=_decode_string_array(
                row["section_hierarchy"], "section hierarchy"
            ),
            start_line=int(row["start_line"]),
            end_line=int(row["end_line"]),
            content=str(row["content"]),
            word_count=int(row["word_count"]),
            char_count=int(row["char_count"]),
            citation=str(row["citation"]),
            size_status=PassageSizeStatus(str(row["size_status"])),
        )


def _last_row_id(cursor: sqlite3.Cursor) -> int:
    row_id = cursor.lastrowid
    if row_id is None:
        raise sqlite3.DatabaseError("SQLite did not return an inserted row ID")
    return row_id


def _validate_source_rows(connection: sqlite3.Connection) -> None:
    for language, source_type, topics, content_digest in connection.execute(
        "SELECT language, source_type, topics, content_digest FROM sources"
    ):
        if language != "en":
            raise ValueError("source language must be 'en'")
        if source_type not in _VALID_SOURCE_TYPES:
            raise ValueError("source type is invalid")
        _decode_string_array(topics, "topics")
        if not isinstance(content_digest, str) or not re.fullmatch(
            r"[0-9a-f]{64}", content_digest
        ):
            raise ValueError("source content digest is invalid")


def _validate_passage_rows(connection: sqlite3.Connection) -> None:
    rows = connection.execute(
        """
        SELECT section_hierarchy, start_line, end_line, content,
               word_count, char_count, size_status
        FROM passages
        """
    ).fetchall()
    for row in rows:
        _decode_string_array(row["section_hierarchy"], "section hierarchy")
        start_line = int(row["start_line"])
        end_line = int(row["end_line"])
        content = str(row["content"])
        word_count = int(row["word_count"])
        char_count = int(row["char_count"])
        size_status = str(row["size_status"])
        if start_line < 1 or end_line < start_line:
            raise ValueError("passage line range is invalid")
        if not content.strip():
            raise ValueError("passage content cannot be empty")
        if word_count != len(re.findall(r"\S+", content)):
            raise ValueError("passage word count does not match content")
        if char_count != len(content):
            raise ValueError("passage character count does not match content")
        if size_status not in _VALID_SIZE_STATUSES:
            raise ValueError("passage size status is invalid")


def _validate_fts_rows(connection: sqlite3.Connection) -> None:
    rows = connection.execute(
        """
        SELECT s.title AS p_title, s.category AS p_category,
               s.topics AS p_topics, p.content AS p_content,
               f.title AS f_title, f.category AS f_category,
               f.topics AS f_topics, f.content AS f_content
        FROM passages p
        JOIN sources s ON s.id = p.source_id
        JOIN passages_fts f ON f.rowid = p.id
        """
    ).fetchall()
    for row in rows:
        topics = " ".join(_decode_string_array(row["p_topics"], "topics"))
        if (
            str(row["p_title"]) != str(row["f_title"])
            or str(row["p_category"]) != str(row["f_category"])
            or topics != str(row["f_topics"])
            or str(row["p_content"]) != str(row["f_content"])
        ):
            raise ValueError("FTS rows do not match source passage content")


def _decode_string_array(raw_value: object, field_name: str) -> tuple[str, ...]:
    if not isinstance(raw_value, str):
        raise TypeError(f"{field_name} must be stored as JSON text")
    try:
        decoded = json.loads(raw_value)
    except json.JSONDecodeError as error:
        raise ValueError(f"{field_name} is not valid JSON") from error
    if not isinstance(decoded, list) or not all(
        isinstance(item, str) for item in decoded
    ):
        raise ValueError(f"{field_name} must be a JSON array of strings")
    return tuple(decoded)


def _table_count(connection: sqlite3.Connection, table_name: str) -> int:
    row = connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
    if not row:
        raise sqlite3.DatabaseError(f"could not count rows in {table_name}")
    return int(row[0])
