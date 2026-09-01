"""Frontmatter parsing tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from main.utils.kb_engine.errors import InvalidKnowledgeSourceError
from main.utils.kb_engine.frontmatter import (
    FrontmatterManager,
    KnowledgeSource,
    parse_frontmatter,
)
from main.utils.kb_engine.taxonomy import TaxonomyRegistry


class TestFrontmatterManager(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.kb_dir = Path(self.temp_dir.name) / "Knowledge_base"
        self.kb_dir.mkdir()
        TaxonomyRegistry.generate_taxonomy_markdown(self.kb_dir)
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

    def test_knowledge_source_domain_module(self) -> None:
        source_file = self.kb_dir / "Articles" / "nutrition" / "test_source.md"
        source_file.parent.mkdir(parents=True, exist_ok=True)
        initial_content = """---
title: Initial Title
category: nutrition
topics:
  - Carbohydrate_ratio
summary: Initial summary.
author: Jane Doe
source: https://example.com/paper
date: '2026-01-01'
---

# Initial Title

Body text here.
"""
        source_file.write_text(initial_content, encoding="utf-8")
        taxonomy = TaxonomyRegistry(self.kb_dir)
        source = KnowledgeSource.from_path(source_file, self.kb_dir, taxonomy)

        self.assertEqual(source.title, "Initial Title")
        self.assertEqual(source.category, "nutrition")
        self.assertEqual(source.topics, ["Carbohydrate_fueling_and_gut_training"])
        self.assertEqual(source.author, "Jane Doe")
        self.assertEqual(source.source, "https://example.com/paper")

        # Mutate and save
        source.update_metadata(
            category="training",
            topics=["VO2max_and_aerobic_hiit", "Zone2_and_endurance_base"],
            summary="Updated summary.",
            key_takeaways=["Takeaway 1", "Takeaway 2"],
        )
        source.save()

        # Reload from disk and verify
        reloaded = KnowledgeSource.from_path(source_file, self.kb_dir, taxonomy)
        self.assertEqual(reloaded.category, "training")
        self.assertEqual(
            reloaded.topics,
            ["VO2max_and_aerobic_hiit", "Zone2_and_endurance_base"],
        )
        self.assertEqual(reloaded.summary, "Updated summary.")
        self.assertEqual(reloaded.author, "Jane Doe")
        self.assertEqual(reloaded.key_takeaways, ["Takeaway 1", "Takeaway 2"])
        self.assertIn("# Initial Title\n\nBody text here.", reloaded.body)

    def test_invalid_taxonomy_mutation_raises_error(self) -> None:
        source_file = self.kb_dir / "Articles" / "nutrition" / "invalid_tax.md"
        source_file.parent.mkdir(parents=True, exist_ok=True)
        source_file.write_text(
            "---\n"
            "title: T\n"
            "category: nutrition\n"
            "topics: [Carbohydrate_fueling_and_gut_training]\n"
            "summary: S\n"
            "---\n\nBody",
            encoding="utf-8",
        )
        taxonomy = TaxonomyRegistry(self.kb_dir)
        source = KnowledgeSource.from_path(source_file, self.kb_dir, taxonomy)

        from main.utils.kb_engine.errors import InvalidTaxonomyError

        with self.assertRaises(InvalidTaxonomyError):
            source.update_metadata(category="invented_category")

        with self.assertRaises(InvalidTaxonomyError):
            source.update_metadata(topics=["invented_topic_slug"])

    def test_dry_run_and_permission_preservation(self) -> None:
        source_file = self.kb_dir / "Articles" / "nutrition" / "perm_test.md"
        source_file.parent.mkdir(parents=True, exist_ok=True)
        initial_content = (
            "---\ntitle: Perm Test\ncategory: nutrition\n"
            "topics:\n  - Carbohydrate_fueling_and_gut_training\n"
            "summary: Initial summary.\ncustom_extra: preserved_value\n"
            "---\n\nExact markdown body with *formatting*.\n"
        )
        source_file.write_text(initial_content, encoding="utf-8")
        import os

        os.chmod(source_file, 0o600)

        taxonomy = TaxonomyRegistry(self.kb_dir)
        source = KnowledgeSource.from_path(source_file, self.kb_dir, taxonomy)

        # Dry run save
        source.update_metadata(summary="Dry run summary")
        source.save(dry_run=True)
        reloaded_dry = source_file.read_text(encoding="utf-8")
        self.assertEqual(reloaded_dry, initial_content)

        # Real save
        source.save(dry_run=False)
        reloaded_text = source_file.read_text(encoding="utf-8")
        self.assertIn("Dry run summary", reloaded_text)
        self.assertIn("custom_extra: preserved_value", reloaded_text)
        self.assertTrue(
            reloaded_text.endswith("\nExact markdown body with *formatting*.\n")
        )
        self.assertEqual(os.stat(source_file).st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
