"""Unit tests for domain query preprocessor."""

from __future__ import annotations

import unittest

from main.utils.kb_engine.query_preprocessor import (
    expand_domain_synonyms,
    extract_searchable_terms,
    preprocess_query,
)


class TestQueryPreprocessor(unittest.TestCase):
    def test_extract_searchable_terms_filters_stopwords(self) -> None:
        raw = "How to increase my FTP over a 12-week block?"
        terms = extract_searchable_terms(raw)
        self.assertIn("ftp", terms)
        self.assertIn("increase", terms)
        self.assertIn("block", terms)
        self.assertNotIn("how", terms)
        self.assertNotIn("to", terms)
        self.assertNotIn("my", terms)
        self.assertNotIn("over", terms)
        self.assertNotIn("a", terms)

    def test_domain_synonym_expansion(self) -> None:
        terms = ["ftp"]
        expanded = expand_domain_synonyms(terms)
        self.assertIn("ftp", expanded)
        self.assertTrue(
            any("threshold" in t.lower() or "functional" in t.lower() for t in expanded)
        )

    def test_preprocess_query_produces_valid_fts_syntax(self) -> None:
        fts_query = preprocess_query("How to train VO2max with 4x8 intervals?")
        self.assertTrue(len(fts_query) > 0)
        self.assertIn('"vo2max"', fts_query.lower())
        self.assertNotIn('"how"', fts_query.lower())
        self.assertNotIn('"to"', fts_query.lower())
        self.assertNotIn('"with"', fts_query.lower())

    def test_empty_or_stopword_only_query_fallback(self) -> None:
        # If user queries only stop words, fallback gracefully so query doesn't crash
        fts_query = preprocess_query("what is it")
        self.assertTrue(len(fts_query) > 0)

    def test_filters_broad_conversational_fillers(self) -> None:
        terms = extract_searchable_terms(
            "Please explain what's already been given about FTP"
        )
        self.assertEqual(terms, ["ftp"])

    def test_preserves_meaning_bearing_query_terms(self) -> None:
        terms = extract_searchable_terms(
            "Why not compare 4x8 versus 4x4 before threshold training?"
        )
        self.assertEqual(
            terms,
            ["not", "4x8", "versus", "4x4", "before", "threshold", "training"],
        )


if __name__ == "__main__":
    unittest.main()
