"""
Unit tests for KBEngine deep module.
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from main.utils.kb_engine import KBEngine

class TestKBEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = KBEngine()

    def test_search_fts(self):
        results = self.engine.search("VO2max cardiac hypertrophy", top_k=3)
        self.assertGreater(len(results), 0)
        self.assertIn("VO2max", results[0]["title"] + " " + results[0]["content"])
        self.assertIn("bm25_score", results[0])

    def test_format_llm_context(self):
        results = self.engine.search("Zone 2 fat oxidation", top_k=2)
        formatted = self.engine.format_llm_context(results)
        self.assertIn("Knowledge Base Context", formatted)
        self.assertIn("Source Link:", formatted)

    def test_build_sitemap(self):
        sitemap = self.engine.build_sitemap()
        self.assertIn("Master Knowledge Base Index", sitemap)
        self.assertIn("Document Catalog by Category", sitemap)

    def test_health_validator(self):
        report = self.engine.validate()
        self.assertTrue(report["is_healthy"])
        self.assertGreater(report["total_docs"], 0)
        self.assertEqual(len(report["errors"]), 0)

if __name__ == "__main__":
    unittest.main()
