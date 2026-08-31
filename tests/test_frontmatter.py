"""Frontmatter parsing tests."""

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

    def test_parse_valid_frontmatter(self) -> None:
        source = self.kb_dir / "Articles" / "nutrition" / "fueling.md"
        source.parent.mkdir(parents=True)
        content = """---
title: Fueling Strategies
language: en
category: nutrition
topics:
  - Carbohydrate_ratio
source: Test journal
author: Test Researcher
date: 2026-08-20
summary: Glucose and fructose carbohydrate intake.
---

# Fueling Strategies

Evidence body content.
"""
        source.write_text(content, encoding="utf-8")
        metadata, body = self.manager.parse_document(source)

        self.assertEqual(metadata["title"], "Fueling Strategies")
        self.assertEqual(metadata["category"], "nutrition")
        self.assertEqual(metadata["topics"], ["Carbohydrate_ratio"])
        self.assertEqual(metadata["language"], "en")
        self.assertEqual(metadata["source"], "Test journal")
        self.assertEqual(metadata["author"], "Test Researcher")
        self.assertEqual(str(metadata["date"]), "2026-08-20")
        self.assertIn("Glucose and fructose", metadata["summary"])
        self.assertIn("# Fueling Strategies", body)

    def test_parse_unclosed_frontmatter_raises_error(self) -> None:
        content = """---
title: Unclosed
category: nutrition
"""
        with self.assertRaises(InvalidKnowledgeSourceError):
            parse_frontmatter(content, "Articles/unclosed.md")

    def test_parse_invalid_yaml_raises_error(self) -> None:
        content = """---
title: [unbalanced brackets
category: nutrition
---
"""
        with self.assertRaises(InvalidKnowledgeSourceError):
            parse_frontmatter(content, "Articles/invalid.md")

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

