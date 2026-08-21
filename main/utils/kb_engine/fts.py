"""Transactional SQLite FTS5 index over citation-stable Evidence Passages."""

from __future__ import annotations

import json
import os
import re
import sqlite3
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .chunker import StructureAwareChunker
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
    IndexState,
    IndexStatus,
    PassageSizeStatus,
)
from .query_preprocessor import preprocess_query
from .sync import build_corpus_manifest

_SCHEMA_VERSION = "2"
_VALID_SOURCE_TYPES = frozenset({"article", "podcast", "book"})
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

    def synchronize(self) -> IndexStatus:
        manifest = build_corpus_manifest(self.kb_dir)
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
            passage_count = self._build_database(temporary_path, manifest)
            if build_corpus_manifest(self.kb_dir).digest != manifest.digest:
                raise CorpusChangedDuringSyncError
            os.replace(temporary_path, self.db_path)
        except sqlite3.DatabaseError as error:
            raise InvalidIndexError from error
        except OSError as error:
            raise InvalidIndexPathError(
                self.db_path, f"the index could not be replaced: {error}"
            ) from error
        finally:
            temporary_path.unlink(missing_ok=True)

        return IndexStatus(
            state=IndexState.FRESH,
            document_count=manifest.document_count,
            passage_count=passage_count,
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
        limit: int = 5,
    ) -> tuple[EvidenceSearchResult, ...]:
        if not 1 <= limit <= 20:
            raise InvalidSearchError("limit must be between 1 and 20")
        tokens = [token for token in re.findall(r"\w+", query) if len(token) > 1]
        if not tokens:
            raise InvalidSearchError("query must contain at least one searchable term")
        self._require_fresh_index()
        fts_query = preprocess_query(query)

        sql = f"""
            SELECT {_PASSAGE_COLUMNS}, bm25(passages_fts, 5.0, 1.0, 2.0, 4.0, 2.0, 1.0) AS lexical_rank
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

    def _build_database(self, path: Path, manifest: CorpusManifest) -> int:
        with sqlite3.connect(path) as connection:
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            self._create_schema(connection)
            passage_count = 0
            for rel_path, source_digest in manifest.source_digests:
                source_path = self.kb_dir / rel_path
                passages = self.chunker.chunk_document(
                    source_path,
                    expected_digest=source_digest,
                )
                if not passages:
                    raise InvalidKnowledgeSourceError(
                        rel_path,
                        "chunking produced no Evidence Passages",
                    )
                source_id = self._insert_source(connection, passages[0])
                for passage in passages:
                    passage_count += 1
                    self._insert_passage(connection, source_id, passage)

            metadata = {
                "schema_version": _SCHEMA_VERSION,
                "corpus_digest": manifest.digest,
                "document_count": str(manifest.document_count),
                "passage_count": str(passage_count),
            }
            connection.executemany(
                "INSERT INTO meta (key, value) VALUES (?, ?)", metadata.items()
            )
            connection.commit()
            snapshot = self._inspect_database(connection)
        return snapshot.passage_count

    @staticmethod
    def _create_schema(connection: sqlite3.Connection) -> None:
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
                source TEXT NOT NULL
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

            CREATE INDEX passages_source_id ON passages(source_id);
            """
        )

    @staticmethod
    def _insert_source(connection: sqlite3.Connection, passage: EvidencePassage) -> int:
        cursor = connection.execute(
            """
                INSERT INTO sources (
                    slug, rel_path, title, author, language,
                    source_type, category, topics, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            ),
        )
        return _last_row_id(cursor)

    @staticmethod
    def _insert_passage(
        connection: sqlite3.Connection,
        source_id: int,
        passage: EvidencePassage,
    ) -> None:
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
        connection.execute(
            """
                INSERT INTO passages_fts (
                    rowid, title, author, category, topics, section_path, content
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                _last_row_id(cursor),
                passage.title,
                passage.author,
                passage.category,
                " ".join(passage.topics),
                passage.section_path,
                passage.content,
            ),
        )

    @staticmethod
    def _inspect_database(connection: sqlite3.Connection) -> _IndexSnapshot:
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

        try:
            expected_sources = int(metadata["document_count"])
            expected_passages = int(metadata["passage_count"])
        except (KeyError, ValueError) as error:
            raise sqlite3.DatabaseError("index metadata is incomplete") from error
        if source_count != expected_sources:
            raise sqlite3.DatabaseError("source count does not match index metadata")
        if passage_count != expected_passages or fts_count != passage_count:
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
    for language, source_type, topics in connection.execute(
        "SELECT language, source_type, topics FROM sources"
    ):
        if language != "en":
            raise ValueError("source language must be 'en'")
        if source_type not in _VALID_SOURCE_TYPES:
            raise ValueError("source type is invalid")
        _decode_string_array(topics, "topics")


def _validate_passage_rows(connection: sqlite3.Connection) -> None:
    rows = connection.execute(
        """
        SELECT section_hierarchy, start_line, end_line, content,
               word_count, char_count, size_status
        FROM passages
        """
    )
    for hierarchy, start, end, content, words, characters, size_status in rows:
        _decode_string_array(hierarchy, "section hierarchy")
        start_line = _stored_integer(start, "start line")
        end_line = _stored_integer(end, "end line")
        word_count = _stored_integer(words, "word count")
        char_count = _stored_integer(characters, "character count")
        if start_line < 1 or end_line < start_line:
            raise ValueError("passage line range is invalid")
        if not isinstance(content, str) or not content:
            raise ValueError("passage content must be non-empty text")
        if word_count != len(content.split()) or char_count != len(content):
            raise ValueError("passage measurements do not match its content")
        if size_status not in _VALID_SIZE_STATUSES:
            raise ValueError("passage size status is invalid")


def _validate_fts_rows(connection: sqlite3.Connection) -> None:
    rows = connection.execute(
        """
        SELECT f.title, f.author, f.category, f.topics, f.section_path, f.content,
               s.title, s.author, s.category, s.topics,
               p.section_hierarchy, p.content
        FROM passages_fts f
        JOIN passages p ON p.id = f.rowid
        JOIN sources s ON s.id = p.source_id
        """
    )
    for row in rows:
        expected = (
            row[6],
            row[7],
            row[8],
            " ".join(_decode_string_array(row[9], "topics")),
            " > ".join(_decode_string_array(row[10], "section hierarchy")),
            row[11],
        )
        if tuple(row[:6]) != expected:
            raise ValueError("passage search payload differs from stored evidence")


def _stored_integer(value: object, field_name: str) -> int:
    if not isinstance(value, int):
        raise ValueError(f"{field_name} must be stored as an integer")
    return value


def _decode_string_array(value: object, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be stored as JSON text")
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError as error:
        raise ValueError(f"{field_name} contains malformed JSON") from error
    if not isinstance(decoded, list) or not all(
        isinstance(item, str) for item in decoded
    ):
        raise ValueError(f"{field_name} must be a JSON array of strings")
    return tuple(decoded)


def _table_count(
    connection: sqlite3.Connection,
    table: Literal["sources", "passages", "passages_fts"],
) -> int:
    row = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    if row is None:
        raise sqlite3.DatabaseError(f"could not count index table: {table}")
    return int(row[0])
