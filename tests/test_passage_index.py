"""Contract tests for the explicit, passage-level SQLite index."""

from __future__ import annotations

import hashlib
import sqlite3
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

from main.utils.kb_engine.errors import (
    CorpusChangedDuringSyncError,
    IndexNotBuiltError,
    InvalidIndexError,
    InvalidKnowledgeSourceError,
    InvalidSearchError,
    StaleIndexError,
)
from main.utils.kb_engine.fts import PassageIndex


class TestPassageIndex(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.kb_dir = self.root / "Knowledge_base"
        self.db_path = self.root / "passages.sqlite"
        self.kb_dir.mkdir()

        self.taxonomy_path = self.kb_dir / "TAXONOMY.md"
        self.taxonomy_path.write_text(
            textwrap.dedent(
                """\
                # Taxonomy

                ### 1. `physiology`
                  - `VO2max`
                  - `Aerobic_base`
                  - `Shared`

                ### 2. `nutrition`
                  - `VO2max_Advanced`
                  - `Shared`
                """
            ),
            encoding="utf-8",
        )
        (self.kb_dir / "INDEX.md").write_text(
            "# Generated catalogue\n\nThis file is not a Knowledge Source.\n",
            encoding="utf-8",
        )

        self.alpha_path = self._write_source(
            "Articles/alpha.md",
            title="Alpha Oxygen Study",
            category="physiology",
            topics=("VO2max", "Shared"),
            marker="mitochondrialsignature",
        )
        self.alpha_extended_path = self._write_source(
            "Articles/alpha-extended.md",
            title="Alpha Nutrition Study",
            category="nutrition",
            topics=("VO2max_Advanced", "Shared"),
            marker="glycogensignature",
        )
        self.beta_path = self._write_source(
            "Notes/beta.md",
            title="Beta Aerobic Study",
            category="physiology",
            topics=("Aerobic_base", "Shared"),
            marker="capillarysignature",
        )
        self.index = PassageIndex(self.kb_dir, self.db_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _write_source(
        self,
        relative_path: str,
        *,
        title: str,
        category: str,
        topics: tuple[str, ...],
        marker: str,
    ) -> Path:
        path = self.kb_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        yaml_topics = "\n".join(f"  - {topic}" for topic in topics)
        paragraph = " ".join(
            [
                f"cadencemarker {marker} describes a controlled endurance response",
                "with repeatable workload observations and careful athlete monitoring",
                "while investigators compare adaptation signals across training blocks",
            ]
            * 4
        )
        path.write_text(
            f"""---
title: {title}
author: Test Researcher
language: en
category: {category}
topics:
{yaml_topics}
summary: A deliberately small source used by passage-index tests.
source: Local test journal
---

# {title}

## Findings

{paragraph}.
""",
            encoding="utf-8",
        )
        return path

    def _assert_state(self, expected: str):
        status = self.index.status()
        self.assertEqual(status.state.value, expected)
        return status

    def _assert_stale(self) -> None:
        status = self._assert_state("stale")
        self.assertNotEqual(status.current_digest, status.indexed_digest)
        with self.assertRaises(StaleIndexError) as caught:
            self.index.search("cadencemarker")
        self.assertEqual(caught.exception.code, "stale_index")

    def _assert_invalid_index(self) -> None:
        self._assert_state("invalid")
        with self.assertRaises(InvalidIndexError):
            self.index.search("cadencemarker")
        with self.assertRaises(InvalidIndexError):
            self.index.get_passage("any-chunk")

    def _corrupt_index(self, statement: str) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("PRAGMA ignore_check_constraints = ON")
            connection.execute(statement)

    def test_missing_index_requires_explicit_synchronization(self) -> None:
        status = self._assert_state("missing")
        self.assertEqual(status.document_count, 3)
        self.assertEqual(status.passage_count, 0)
        self.assertIsNone(status.indexed_digest)
        self.assertRegex(status.current_digest, r"^[0-9a-f]{64}$")
        self.assertFalse(self.db_path.exists())

        with self.assertRaises(IndexNotBuiltError) as search_error:
            self.index.search("cadencemarker")
        self.assertEqual(search_error.exception.code, "missing_index")

        with self.assertRaises(IndexNotBuiltError) as passage_error:
            self.index.get_passage("not-a-real-chunk")
        self.assertEqual(passage_error.exception.code, "missing_index")
        self.assertEqual(IndexNotBuiltError.code, "missing_index")
        self.assertFalse(self.db_path.exists())

    def test_invalid_search_is_rejected_before_index_freshness_work(self) -> None:
        with self.assertRaises(InvalidSearchError) as limit_error:
            self.index.search("cadencemarker", limit=0)
        self.assertEqual(limit_error.exception.code, "invalid_search")

        with self.assertRaises(InvalidSearchError) as query_error:
            self.index.search("!? --")
        self.assertIn("searchable term", str(query_error.exception))
        self.assertFalse(self.db_path.exists())

    def test_synchronize_builds_the_passage_schema_and_reports_counts(self) -> None:
        status = self.index.synchronize()

        self.assertEqual(status.state.value, "fresh")
        self.assertEqual(status.document_count, 3)
        self.assertGreaterEqual(status.passage_count, 3)
        self.assertEqual(status.current_digest, status.indexed_digest)
        self.assertTrue(self.db_path.is_file())

        with sqlite3.connect(self.db_path) as connection:
            objects = dict(
                connection.execute(
                    "SELECT name, type FROM sqlite_schema "
                    "WHERE name NOT LIKE 'sqlite_%'"
                )
            )
            self.assertTrue(
                {"meta", "sources", "passages", "passages_fts"}.issubset(objects)
            )
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM sources").fetchone()[0], 3
            )
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM passages").fetchone()[0],
                status.passage_count,
            )
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM passages_fts").fetchone()[0],
                status.passage_count,
            )
            meta_rows = connection.execute("SELECT * FROM meta").fetchall()
            self.assertIn(status.indexed_digest, repr(meta_rows))
            self.assertEqual(
                connection.execute("PRAGMA integrity_check").fetchone()[0], "ok"
            )

        refreshed = self.index.status()
        self.assertEqual(refreshed.state.value, "fresh")
        self.assertEqual(refreshed.document_count, status.document_count)
        self.assertEqual(refreshed.passage_count, status.passage_count)

    def test_corpus_digest_is_sha256_and_deterministic(self) -> None:
        first = self.index.status().current_digest
        second = PassageIndex(self.kb_dir, self.db_path).status().current_digest

        self.assertRegex(first, r"^[0-9a-f]{64}$")
        self.assertEqual(second, first)
        first_sync = self.index.synchronize()
        second_sync = self.index.synchronize()
        self.assertEqual(first_sync.current_digest, first)
        self.assertEqual(first_sync.indexed_digest, first)
        self.assertEqual(second_sync.current_digest, first)
        self.assertEqual(second_sync.indexed_digest, first)

    def test_synchronize_supplies_each_source_digest_to_the_chunker(self) -> None:
        chunk_document = self.index.chunker.chunk_document
        received_digests: dict[str, str] = {}

        def record_digest(source_path: Path, *, expected_digest: str):
            relative_path = source_path.relative_to(self.index.kb_dir).as_posix()
            received_digests[relative_path] = expected_digest
            return chunk_document(source_path)

        with patch.object(
            self.index.chunker,
            "chunk_document",
            side_effect=record_digest,
        ):
            self.index.synchronize()

        expected_digests = {
            path.resolve().relative_to(self.index.kb_dir).as_posix(): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in (self.alpha_path, self.alpha_extended_path, self.beta_path)
        }
        self.assertEqual(received_digests, expected_digests)

    def test_search_reads_the_existing_index_without_rebuilding_it(self) -> None:
        self.index.synchronize()
        database_hash = hashlib.sha256(self.db_path.read_bytes()).digest()
        database_mtime = self.db_path.stat().st_mtime_ns

        with patch.object(
            PassageIndex,
            "synchronize",
            side_effect=AssertionError("search must not synchronize implicitly"),
        ):
            results = self.index.search("cadencemarker", limit=2)

        self.assertIsInstance(results, tuple)
        self.assertEqual(len(results), 2)
        self.assertTrue(
            all(isinstance(result.lexical_score, float) for result in results)
        )
        self.assertEqual(
            hashlib.sha256(self.db_path.read_bytes()).digest(), database_hash
        )
        self.assertEqual(self.db_path.stat().st_mtime_ns, database_mtime)

    def test_failed_rebuild_preserves_existing_database_transactionally(
        self,
    ) -> None:
        self.index.synchronize()
        original_beta = self.beta_path.read_text(encoding="utf-8")
        indexed_result = self.index.search("mitochondrialsignature")[0]
        original_database = self.db_path.read_bytes()
        self.beta_path.write_text(
            original_beta + "\nA corpus change that requires synchronization.\n",
            encoding="utf-8",
        )
        chunk_document = self.index.chunker.chunk_document

        def fail_on_beta(source_path: Path, *, expected_digest: str):
            if source_path.resolve() == self.beta_path.resolve():
                raise RuntimeError("simulated chunking failure")
            return chunk_document(source_path, expected_digest=expected_digest)

        with (
            patch.object(
                self.index.chunker,
                "chunk_document",
                side_effect=fail_on_beta,
            ),
            self.assertRaisesRegex(RuntimeError, "simulated chunking failure"),
        ):
            self.index.synchronize()

        self.assertEqual(self.db_path.read_bytes(), original_database)
        self._assert_stale()

        self.beta_path.write_text(original_beta, encoding="utf-8")
        self._assert_state("fresh")
        self.assertEqual(
            self.index.get_passage(indexed_result.passage.chunk_id),
            indexed_result.passage,
        )

    def test_source_without_passages_fails_without_replacing_the_index(self) -> None:
        self.index.synchronize()
        original_database = self.db_path.read_bytes()
        chunk_document = self.index.chunker.chunk_document

        def empty_beta(source_path: Path, *, expected_digest: str):
            if source_path.resolve() == self.beta_path.resolve():
                return ()
            return chunk_document(source_path, expected_digest=expected_digest)

        with (
            patch.object(
                self.index.chunker,
                "chunk_document",
                side_effect=empty_beta,
            ),
            self.assertRaises(InvalidKnowledgeSourceError) as caught,
        ):
            self.index.synchronize()

        self.assertIn("Notes/beta.md", str(caught.exception))
        self.assertIn("no Evidence Passages", str(caught.exception))
        self.assertEqual(self.db_path.read_bytes(), original_database)

    def test_synchronize_translates_sqlite_failures_to_an_index_error(self) -> None:
        with (
            patch.object(
                PassageIndex,
                "_create_schema",
                side_effect=sqlite3.DatabaseError("simulated SQLite failure"),
            ),
            self.assertRaises(InvalidIndexError) as caught,
        ):
            self.index.synchronize()

        self.assertEqual(caught.exception.code, "invalid_index")
        self.assertFalse(self.db_path.exists())

    def test_corpus_change_during_sync_preserves_existing_database(self) -> None:
        self.index.synchronize()
        original_database = self.db_path.read_bytes()
        chunk_document = self.index.chunker.chunk_document
        original_alpha = self.alpha_path.read_text(encoding="utf-8")

        def mutate_during_build(source_path: Path, *, expected_digest: str):
            passages = chunk_document(source_path, expected_digest=expected_digest)
            if source_path.resolve() == self.beta_path.resolve():
                self.alpha_path.write_text(
                    original_alpha + "\nConcurrent corpus edit.\n",
                    encoding="utf-8",
                )
            return passages

        with (
            patch.object(
                self.index.chunker,
                "chunk_document",
                side_effect=mutate_during_build,
            ),
            self.assertRaises(CorpusChangedDuringSyncError),
        ):
            self.index.synchronize()

        self.assertEqual(self.db_path.read_bytes(), original_database)
        self._assert_state("stale")

    def test_missing_fts_table_is_reported_as_an_invalid_index(self) -> None:
        self.index.synchronize()
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("DROP TABLE passages_fts")

        self._assert_state("invalid")
        with self.assertRaises(InvalidIndexError) as caught:
            self.index.search("cadencemarker")
        self.assertEqual(caught.exception.code, "invalid_index")

    def test_malformed_topics_json_is_reported_as_an_invalid_index(self) -> None:
        self.index.synchronize()
        self._corrupt_index("UPDATE sources SET topics = '{'")

        self._assert_invalid_index()

    def test_fts_payload_tampering_is_reported_as_an_invalid_index(self) -> None:
        self.index.synchronize()
        self._corrupt_index("UPDATE passages_fts SET content = 'poisonterm'")

        self._assert_invalid_index()

    def test_topics_must_be_a_json_array_of_strings(self) -> None:
        for stored_topics in ("{}", '["valid", 1]'):
            with self.subTest(stored_topics=stored_topics):
                self.index.synchronize()
                self._corrupt_index(f"UPDATE sources SET topics = '{stored_topics}'")

                self._assert_invalid_index()

    def test_section_hierarchy_must_be_a_json_array_of_strings(self) -> None:
        for stored_hierarchy in ("{", "{}", '["Findings", 1]'):
            with self.subTest(stored_hierarchy=stored_hierarchy):
                self.index.synchronize()
                self._corrupt_index(
                    f"UPDATE passages SET section_hierarchy = '{stored_hierarchy}'"
                )

                self._assert_invalid_index()

    def test_index_rejects_invalid_domain_values(self) -> None:
        corruptions = (
            ("language", "UPDATE sources SET language = 'it'"),
            ("source type", "UPDATE sources SET source_type = 'essay'"),
            ("size status", "UPDATE passages SET size_status = 'unbounded'"),
        )
        for field_name, statement in corruptions:
            with self.subTest(field_name=field_name):
                self.index.synchronize()
                self._corrupt_index(statement)

                self._assert_invalid_index()

    def test_index_rejects_invalid_passage_measurements(self) -> None:
        corruptions = (
            ("word count", "UPDATE passages SET word_count = word_count + 1"),
            ("word count type", "UPDATE passages SET word_count = 1.5"),
            ("character count", "UPDATE passages SET char_count = char_count + 1"),
            ("start line", "UPDATE passages SET start_line = 0"),
            ("line order", "UPDATE passages SET end_line = start_line - 1"),
        )
        for field_name, statement in corruptions:
            with self.subTest(field_name=field_name):
                self.index.synchronize()
                self._corrupt_index(statement)

                self._assert_invalid_index()

    def test_retrieval_translates_database_decode_and_enum_failures(self) -> None:
        corruptions = (
            ("database", "DROP TABLE passages"),
            ("JSON", "UPDATE sources SET topics = '{'"),
            ("enum", "UPDATE passages SET size_status = 'unbounded'"),
        )
        for failure_type, statement in corruptions:
            with self.subTest(failure_type=failure_type):
                fresh_status = self.index.synchronize()
                chunk_id = self.index.search("cadencemarker")[0].passage.chunk_id
                self._corrupt_index(statement)

                with patch.object(self.index, "status", return_value=fresh_status):
                    with self.assertRaises(InvalidIndexError):
                        self.index.search("cadencemarker")
                    with self.assertRaises(InvalidIndexError):
                        self.index.get_passage(chunk_id)

    def test_editing_a_source_marks_the_index_stale(self) -> None:
        self.index.synchronize()
        self.alpha_path.write_text(
            self.alpha_path.read_text(encoding="utf-8") + "\nEdited evidence.\n",
            encoding="utf-8",
        )
        self._assert_stale()

    def test_adding_a_source_marks_the_index_stale(self) -> None:
        self.index.synchronize()
        self._write_source(
            "Articles/new-source.md",
            title="New Source",
            category="physiology",
            topics=("VO2max",),
            marker="newsignature",
        )
        self._assert_stale()

    def test_deleting_a_source_marks_the_index_stale(self) -> None:
        self.index.synchronize()
        self.beta_path.unlink()
        self._assert_stale()

    def test_renaming_a_source_marks_the_index_stale(self) -> None:
        self.index.synchronize()
        self.alpha_path.rename(self.alpha_path.with_name("alpha-renamed.md"))
        self._assert_stale()

    def test_taxonomy_change_marks_the_index_stale(self) -> None:
        self.index.synchronize()
        self.taxonomy_path.write_text(
            self.taxonomy_path.read_text(encoding="utf-8")
            + "\n### 3. `metrics`\n  - `FTP`\n",
            encoding="utf-8",
        )
        self._assert_stale()

    def test_index_catalogue_changes_do_not_stale_the_index(self) -> None:
        synchronized = self.index.synchronize()
        catalogue = self.kb_dir / "INDEX.md"
        catalogue.write_text(
            catalogue.read_text(encoding="utf-8") + "\nA generated row changed.\n",
            encoding="utf-8",
        )

        status = self._assert_state("fresh")
        self.assertEqual(status.current_digest, synchronized.current_digest)
        self.assertEqual(status.indexed_digest, synchronized.indexed_digest)
        self.assertTrue(self.index.search("cadencemarker"))

    def test_summary_directory_is_not_part_of_the_curated_corpus(self) -> None:
        self._write_source(
            "Books/_summary/notes.md",
            title="Administrative Summary",
            category="physiology",
            topics=("VO2max",),
            marker="administrativemarker",
        )

        status = self.index.synchronize()

        self.assertEqual(status.document_count, 3)
        self.assertEqual(self.index.search("administrativemarker"), ())

    def test_symbolic_link_source_is_rejected(self) -> None:
        outside = self.root / "outside.md"
        outside.write_text("# Outside evidence\n", encoding="utf-8")
        link = self.kb_dir / "Articles" / "linked.md"
        link.symlink_to(outside)

        with self.assertRaises(InvalidKnowledgeSourceError):
            self.index.synchronize()

    def test_manifest_read_race_is_a_domain_error(self) -> None:
        read_bytes = Path.read_bytes

        def disappear_during_manifest(path: Path) -> bytes:
            if path.resolve() == self.alpha_path.resolve():
                raise FileNotFoundError(path)
            return read_bytes(path)

        with (
            patch.object(Path, "read_bytes", disappear_during_manifest),
            self.assertRaises(CorpusChangedDuringSyncError),
        ):
            self.index.synchronize()

    def test_filters_match_category_topic_and_source_slug_exactly(self) -> None:
        self.index.synchronize()

        by_category = self.index.search(
            "cadencemarker", category="physiology", limit=20
        )
        self.assertEqual(
            {result.passage.source_slug for result in by_category},
            {"Articles/alpha", "Notes/beta"},
        )
        self.assertTrue(
            all(result.passage.category == "physiology" for result in by_category)
        )

        by_topic = self.index.search("cadencemarker", topic="VO2max", limit=20)
        self.assertEqual(
            {result.passage.source_slug for result in by_topic}, {"Articles/alpha"}
        )
        self.assertTrue(all("VO2max" in result.passage.topics for result in by_topic))

        by_source = self.index.search(
            "cadencemarker", source_slug="Articles/alpha", limit=20
        )
        self.assertEqual(
            {result.passage.source_slug for result in by_source}, {"Articles/alpha"}
        )

    def test_get_passage_returns_the_indexed_evidence_passage(self) -> None:
        self.index.synchronize()
        result = next(
            result
            for result in self.index.search("mitochondrialsignature", limit=5)
            if result.passage.source_slug == "Articles/alpha"
        )

        passage = self.index.get_passage(result.passage.chunk_id)

        self.assertEqual(passage, result.passage)
        self.assertEqual(passage.title, "Alpha Oxygen Study")
        self.assertEqual(passage.category, "physiology")
        self.assertEqual(passage.topics, ("VO2max", "Shared"))
        self.assertIn("mitochondrialsignature", passage.content)
        self.assertLessEqual(passage.start_line, passage.end_line)
        self.assertIn(f"#L{passage.start_line}-L{passage.end_line}", passage.citation)


if __name__ == "__main__":
    unittest.main()
