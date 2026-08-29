"""Integration tests for the KBEngine facade."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from main.utils.kb_engine import KBEngine
from main.utils.kb_engine.errors import (
    EmptyCorpusError,
    InvalidIndexPathError,
    InvalidKnowledgeBaseError,
    InvalidKnowledgeSourceError,
    KnowledgeBaseNotFoundError,
    KnowledgeSourceNotFoundError,
)


class TestKBEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.kb_dir = self.root / "Knowledge_base"
        self.article = self.kb_dir / "Articles" / "oxygen.md"
        self.article.parent.mkdir(parents=True)
        (self.kb_dir / "TAXONOMY.md").write_text(
            "# Taxonomy\n\n### 1. `physiology`\n  - `VO2max`\n",
            encoding="utf-8",
        )
        (self.kb_dir / "INDEX.md").write_text("# Empty index\n", encoding="utf-8")
        self.article.write_text(
            """---
title: Oxygen Adaptation
author: Test Researcher
language: en
category: physiology
topics: [VO2max]
source: Test journal
summary: A test source about oxygen adaptation.
---

# Oxygen Adaptation

## Cardiac response

VO2max improves through cardiac output and repeatable endurance training.
""",
            encoding="utf-8",
        )
        self.engine = KBEngine(
            kb_dir=self.kb_dir,
            db_path=self.root / "passages.sqlite",
            index_file=self.kb_dir / "INDEX.md",
        )
        self.engine.build_index()

    def test_search_returns_evidence_passages(self) -> None:
        results = self.engine.search("VO2max cardiac", top_k=3)

        self.assertGreater(len(results), 0)
        self.assertIn("VO2max", results[0].passage.content)
        self.assertGreater(results[0].lexical_score, 0)
        self.assertEqual(results[0].passage.language, "en")

    def test_custom_kb_defaults_stay_with_the_custom_workspace(self) -> None:
        engine = KBEngine(kb_dir=self.kb_dir)

        self.assertEqual(
            engine.db_path,
            (self.root / "main" / ".kb_index.sqlite").resolve(),
        )
        self.assertEqual(engine.index_file, (self.kb_dir / "INDEX.md").resolve())

    def test_default_kb_dir_can_be_configured_for_an_installed_cli(self) -> None:
        with patch.dict(os.environ, {"ENDURANCE_KB_DIR": str(self.kb_dir)}):
            engine = KBEngine()

        self.assertEqual(engine.kb_dir, self.kb_dir.resolve())

    def test_missing_kb_dir_is_rejected_before_reporting_false_health(self) -> None:
        missing = self.root / "missing"

        with self.assertRaises(KnowledgeBaseNotFoundError):
            KBEngine(kb_dir=missing)

    def test_noncanonical_kb_root_is_rejected(self) -> None:
        with self.assertRaises(InvalidKnowledgeBaseError):
            KBEngine(kb_dir=self.article.parent)

    def test_symbolic_link_index_path_is_rejected(self) -> None:
        target = self.root / "target.sqlite"
        target.write_bytes(b"not an index")
        link = self.root / "linked.sqlite"
        link.symlink_to(target)

        with self.assertRaises(InvalidIndexPathError):
            KBEngine(kb_dir=self.kb_dir, db_path=link)

        self.assertEqual(target.read_bytes(), b"not an index")

    def test_empty_corpus_cannot_be_synchronized(self) -> None:
        empty_kb = self.root / "empty" / "Knowledge_base"
        empty_kb.mkdir(parents=True)
        (empty_kb / "TAXONOMY.md").write_text("# Taxonomy\n", encoding="utf-8")
        engine = KBEngine(kb_dir=empty_kb)

        with self.assertRaises(EmptyCorpusError):
            engine.build_index()

    def test_format_llm_context(self) -> None:
        formatted = self.engine.format_llm_context(
            self.engine.search("VO2max cardiac", top_k=2)
        )

        self.assertIn("Knowledge Base Context", formatted)
        self.assertIn(
            "Instruction: Always report and cite the sources in the final output.",
            formatted,
        )
        self.assertIn("Source Link:", formatted)
        self.assertIn("#L", formatted)

    def test_build_sitemap(self) -> None:
        spaced_source = self.article.with_name("oxygen evidence.md")
        self.article.rename(spaced_source)

        sitemap = self.engine.build_sitemap()

        self.assertIn("Master Knowledge Base Index", sitemap)
        self.assertIn("Document Catalog by Category", sitemap)
        self.assertIn(
            "](<Articles/oxygen evidence.md>)",
            sitemap,
        )

    def test_health_validator(self) -> None:
        self.engine.build_sitemap()
        report = self.engine.validate()

        self.assertTrue(report["is_healthy"])
        self.assertEqual(report["total_docs"], 1)
        self.assertEqual(report["errors"], [])

    def test_validation_can_target_one_canonical_source_path(self) -> None:
        self.article.write_text(
            self.article.read_text(encoding="utf-8")
            + "\n[Missing evidence](missing-reference.md)\n",
            encoding="utf-8",
        )

        report = self.engine.validate(source_rel_path="Articles/oxygen.md")

        self.assertEqual(report["total_docs"], 1)
        self.assertEqual(report["errors"], [])
        self.assertTrue(
            any("missing-reference.md" in warning for warning in report["warnings"])
        )
        with self.assertRaises(KnowledgeSourceNotFoundError):
            self.engine.validate(source_rel_path="../oxygen.md")

    def test_malformed_frontmatter_is_reported_without_type_errors(self) -> None:
        self.article.write_text(
            "---\n- title\n- category\n---\n\nMalformed body.\n",
            encoding="utf-8",
        )

        report = self.engine.validate(source_rel_path="Articles/oxygen.md")

        self.assertEqual(report["total_docs"], 1)
        self.assertTrue(any("mapping" in error for error in report["errors"]))
        with self.assertRaises(InvalidKnowledgeSourceError):
            self.engine.build_sitemap()

    def test_validation_enforces_english_and_reports_taxonomy_drift(self) -> None:
        content = self.article.read_text(encoding="utf-8")
        content = content.replace("language: en", "language: it")
        content = content.replace("category: physiology", "category: general")
        content = content.replace("topics: [VO2max]", "topics: [Near_VO2max]")
        self.article.write_text(content, encoding="utf-8")

        report = self.engine.validate(source_rel_path="Articles/oxygen.md")

        self.assertFalse(report["is_healthy"])
        self.assertTrue(any("Language" in error for error in report["errors"]))
        self.assertTrue(
            any("Category 'general'" in warning for warning in report["warnings"])
        )
        self.assertTrue(
            any("Topic 'Near_VO2max'" in warning for warning in report["warnings"])
        )

    def test_validation_and_chunking_share_frontmatter_delimiters(self) -> None:
        content = self.article.read_text(encoding="utf-8")
        content = content.replace("---\n", "---   \n")
        self.article.write_text(content, encoding="utf-8")

        report = self.engine.validate(source_rel_path="Articles/oxygen.md")

        self.assertTrue(report["is_healthy"])
        self.assertEqual(report["errors"], [])


if __name__ == "__main__":
    unittest.main()
