"""Frontmatter inference safety tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from main.utils.kb_engine.errors import InvalidKnowledgeSourceError
from main.utils.kb_engine.frontmatter import FrontmatterManager, parse_frontmatter
from main.utils.kb_engine.taxonomy import TaxonomyRegistry


class TestFrontmatterManager(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.kb_dir = Path(self.temp_dir.name) / "Knowledge_base"
        self.kb_dir.mkdir()
        (self.kb_dir / "TAXONOMY.md").write_text(
            "# Taxonomy\n\n### 1. `nutrition`\n  - `Carbohydrate_ratio`\n",
            encoding="utf-8",
        )
        self.manager = FrontmatterManager(self.kb_dir, TaxonomyRegistry(self.kb_dir))

    def test_carbohydrate_inference_uses_the_canonical_topic(self) -> None:
        source = self.kb_dir / "Articles" / "nutrition" / "fueling.md"
        source.parent.mkdir(parents=True)
        content = "\n".join(
            (
                "# Fueling",
                "Source: Test journal",
                "Author: Test Researcher",
                "Date: 2026-08-20",
                "",
                "Glucose and fructose carbohydrate intake.",
            )
        )

        metadata = self.manager.infer_metadata(content, source)

        self.assertIn("Carbohydrate_ratio", metadata["topics"])
        self.assertNotIn("Glucose_fructose", metadata["topics"])
        self.assertEqual(metadata["language"], "en")
        self.assertNotEqual(metadata["source"], "Knowledge Base")
        self.assertNotEqual(metadata["author"], "Endurance Research")
        self.assertIn("Glucose and fructose", metadata["summary"])

        source.write_text(content, encoding="utf-8")
        self.assertTrue(self.manager.standardize_file(source))
        written_metadata, _body = self.manager.parse_document(source)
        self.assertEqual(written_metadata["source"], "Test journal")
        self.assertEqual(written_metadata["author"], "Test Researcher")
        self.assertEqual(str(written_metadata["date"]), "2026-08-20")

    def test_standardize_refuses_to_invent_a_noncanonical_topic(self) -> None:
        source = self.kb_dir / "Articles" / "misc" / "unknown.md"
        source.parent.mkdir(parents=True)
        original = "# Unclassified note\n\nEvidence without a known taxonomy keyword.\n"
        source.write_text(original, encoding="utf-8")

        with self.assertRaises(InvalidKnowledgeSourceError):
            self.manager.standardize_file(source)

        self.assertEqual(source.read_text(encoding="utf-8"), original)

    def test_indented_yaml_rule_does_not_close_frontmatter(self) -> None:
        content = """---
title: Block Scalar
category: nutrition
topics: [Carbohydrate_ratio]
summary: |
  ---
  A faithful multiline summary.
---

# Evidence
"""

        parsed = parse_frontmatter(content, "Articles/block-scalar.md")

        self.assertTrue(parsed.has_frontmatter)
        self.assertEqual(parsed.metadata["category"], "nutrition")
        self.assertEqual(parsed.metadata["topics"], ["Carbohydrate_ratio"])
        self.assertIn("A faithful multiline summary", parsed.metadata["summary"])
        self.assertEqual(parsed.content_start, 8)
        self.assertTrue(parsed.body.startswith("\n# Evidence"))


if __name__ == "__main__":
    unittest.main()
