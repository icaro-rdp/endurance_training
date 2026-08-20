"""Integration tests for the KBEngine facade."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from main.utils.kb_engine import KBEngine


class TestKBEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.kb_dir = self.root / "Knowledge_base"
        article = self.kb_dir / "Articles" / "oxygen.md"
        article.parent.mkdir(parents=True)
        (self.kb_dir / "TAXONOMY.md").write_text(
            "# Taxonomy\n\n### 1. `physiology`\n  - `VO2max`\n",
            encoding="utf-8",
        )
        (self.kb_dir / "INDEX.md").write_text("# Empty index\n", encoding="utf-8")
        article.write_text(
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

    def test_format_llm_context(self) -> None:
        formatted = self.engine.format_llm_context(
            self.engine.search("VO2max cardiac", top_k=2)
        )

        self.assertIn("Knowledge Base Context", formatted)
        self.assertIn("Source Link:", formatted)
        self.assertIn("#L", formatted)

    def test_build_sitemap(self) -> None:
        sitemap = self.engine.build_sitemap()

        self.assertIn("Master Knowledge Base Index", sitemap)
        self.assertIn("Document Catalog by Category", sitemap)

    def test_health_validator(self) -> None:
        self.engine.build_sitemap()
        report = self.engine.validate()

        self.assertTrue(report["is_healthy"])
        self.assertEqual(report["total_docs"], 1)
        self.assertEqual(report["errors"], [])


if __name__ == "__main__":
    unittest.main()
