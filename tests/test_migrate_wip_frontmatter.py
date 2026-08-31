"""Unit tests for WIP frontmatter migration and taxonomy classifier."""

import tempfile
import unittest
from pathlib import Path

from main.migrate_wip_frontmatter import WIPFrontmatterMigrator
from main.utils.kb_engine.frontmatter import parse_frontmatter
from main.utils.kb_engine.taxonomy import TaxonomyRegistry


class TestWIPFrontmatterMigrator(unittest.TestCase):
    def setUp(self) -> None:
        self.kb_dir = Path("Knowledge_base")
        self.taxonomy = TaxonomyRegistry(self.kb_dir)
        self.migrator = WIPFrontmatterMigrator(self.kb_dir, self.taxonomy)

    def test_normalize_date_formats(self) -> None:
        # Standard ISO
        self.assertEqual(self.migrator.normalize_date("2024-05-12"), "2024-05-12")
        # Unpadded ISO
        self.assertEqual(self.migrator.normalize_date("2024-2-9"), "2024-02-09")
        # Day Month with year in text
        sample_text = "Referenced from study in 2022 and another in 2021."
        self.assertEqual(
            self.migrator.normalize_date("21 Jul", content=sample_text), "2022-07-21"
        )
        # Month Day, Year
        self.assertEqual(self.migrator.normalize_date("October 15, 2023"), "2023-10-15")

    def test_extract_source_and_author(self) -> None:
        content = (
            "# Test Post\n\n"
            "<nav>\n"
            "- Source: [Original Article](https://sparecycles.blog/2021/05/10/testing-guide/)\n"
            "- Author: [Jem Arnold](https://sparecycles.blog/about/)\n"
            "</nav>"
        )
        file_path = Path("Knowledge_base/WIP/Blog/Spare_Cycles/test.md")
        source = self.migrator.extract_source(file_path, content)
        author = self.migrator.extract_author(file_path, {}, content)

        self.assertEqual(
            source, "https://sparecycles.blog/2021/05/10/testing-guide/"
        )
        self.assertEqual(author, "Jem Arnold")

    def test_extract_summary_and_cleaning(self) -> None:
        meta = {
            "description": "5 Ways To Assess Progress\n\n21 Jul\n\nWritten By [Tom Bell](<http://test.com>)\n\nMaximal testing is commonly used by coaches."
        }
        content = "# 5 Ways To Assess Progress\n\nSome body text here."
        summary = self.migrator.extract_summary(
            meta, content, content, "5 Ways To Assess Progress"
        )
        self.assertNotIn("Written By", summary)
        self.assertNotIn("<http", summary)
        self.assertIn("Maximal testing is commonly used", summary)

    def test_extract_key_takeaways_filters_host_links(self) -> None:
        body = (
            "## Key Takeaways\n\n"
            "* Understanding Thresholds: Thresholds signify transition points in metabolic response.\n"
            "* Training in Zone 2 enhances mitochondrial fat oxidation.\n"
            "* [Host Bio - Where fitness meets motherhood](<https://tiredmomruns.com>)\n"
            "* [Breath: The New Science by James Nestor](<https://amazon.com/book>)\n"
        )
        takeaways = self.migrator.extract_key_takeaways(body)
        self.assertIsNotNone(takeaways)
        self.assertEqual(len(takeaways), 2)
        self.assertIn("Understanding Thresholds", takeaways[0])
        self.assertIn("Training in Zone 2", takeaways[1])

    def test_classify_document_topics_and_category(self) -> None:
        # Test HIIT interval topic
        cat, topics = self.migrator.classify_document(
            title="Why Perform Hard-Start VO2max Intervals",
            summary="Hard-start intervals accelerate VO2 kinetics and maximize time at high percentage of VO2max.",
            body="Sprint start pacing accelerates cardiovascular response.",
        )
        self.assertIn(cat, ["training", "physiology"])
        self.assertTrue(
            any(
                t in topics
                for t in ["Fast_start_intervals", "VO2max", "Short_intervals", "Long_intervals"]
            )
        )

        # Test Nutrition topic
        cat_nutr, topics_nutr = self.migrator.classify_document(
            title="Sodium Bicarbonate and Beta-Alanine Fueling Guide",
            summary="Extracellular and intracellular buffering agents improve high-intensity cycling performance.",
            body="Bicarb loading protocol with Maurten system and beta alanine carnosine saturation.",
        )
        self.assertEqual(cat_nutr, "nutrition")
        self.assertIn("Sodium_bicarbonate", topics_nutr)

    def test_full_process_file_validity(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            sample_file = tmp_path / "test_doc.md"
            sample_content = (
                "---\n"
                'title: "35: Higher FTP vs Longer TTE"\n'
                'description: "Community transcript and notes for Empirical Cycling podcast episode Tmt 35."\n'
                "date: 2024-2-20\n"
                'author: "Empirical Cycling Community / Kolie Moore"\n'
                'license: "CC-BY-4.0"\n'
                "---\n\n"
                "# 35: Higher FTP vs Longer TTE\n\n"
                "<abstract lang=\"en\">\n"
                "Community transcript and notes for Empirical Cycling podcast episode Tmt 35.\n"
                "</abstract>\n\n"
                "This educational guide explores FTP versus TTE and how to structure training blocks for threshold extension.\n\n"
                "<nav>\n"
                "- Source: [Original Article](https://lucasvance.github.io/empirical-cycling-community-notes/)\n"
                "- Author: [Empirical Cycling Community / Kolie Moore](https://www.empiricalcycling.com)\n"
                "</nav>\n"
            )
            sample_file.write_text(sample_content, encoding="utf-8")

            res = self.migrator.process_file(sample_file, apply=True)
            self.assertTrue(res.changed)

            # Check new content parseable as valid frontmatter
            new_text = sample_file.read_text(encoding="utf-8")
            parsed = parse_frontmatter(new_text, "test_doc.md")

            self.assertTrue(parsed.has_frontmatter)
            self.assertEqual(parsed.metadata["language"], "en")
            self.assertEqual(parsed.metadata["date"], "2024-02-20")
            self.assertIn("TTA_TTE", parsed.metadata["topics"])
            self.assertNotIn("<abstract", parsed.body)
            self.assertNotIn("<nav", parsed.body)


if __name__ == "__main__":
    unittest.main()
