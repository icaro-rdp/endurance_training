"""Unit tests for Hybrid Search & Reciprocal Rank Fusion."""

from __future__ import annotations

import unittest

from main.utils.kb_engine.hybrid import (
    reciprocal_rank_fusion,
    SemanticVectorizer,
)
from main.utils.kb_engine.models import EvidencePassage, EvidenceSearchResult, PassageSizeStatus


def _dummy_passage(chunk_id: str, title: str, content: str) -> EvidencePassage:
    return EvidencePassage(
        chunk_id=chunk_id,
        source_slug=f"Sources/{chunk_id}",
        rel_path=f"Sources/{chunk_id}.md",
        title=title,
        author="Author",
        language="en",
        source_type="article",
        category="hiit",
        topics=("VO2max",),
        source="Test Source",
        section_hierarchy=("Header",),
        start_line=10,
        end_line=25,
        content=content,
        word_count=len(content.split()),
        char_count=len(content),
        citation=f"Sources/{chunk_id}.md#L10-L25",
        size_status=PassageSizeStatus.WITHIN_POLICY,
    )


class TestHybridRetrieval(unittest.TestCase):
    def test_reciprocal_rank_fusion_merges_multiple_rankings(self) -> None:
        p1 = _dummy_passage("c1", "Passage One", "Content one")
        p2 = _dummy_passage("c2", "Passage Two", "Content two")
        p3 = _dummy_passage("c3", "Passage Three", "Content three")

        list_a = [EvidenceSearchResult(p1, 10.0), EvidenceSearchResult(p2, 5.0)]
        list_b = [EvidenceSearchResult(p2, 8.0), EvidenceSearchResult(p3, 4.0)]

        fused = reciprocal_rank_fusion([list_a, list_b], k=60, limit=3)
        self.assertEqual(len(fused), 3)
        # p2 appears in both rankings (rank 2 in A, rank 1 in B), so its fused score is highest!
        self.assertEqual(fused[0].passage.chunk_id, "c2")
        self.assertEqual(fused[1].passage.chunk_id, "c1")
        self.assertEqual(fused[2].passage.chunk_id, "c3")

    def test_semantic_vectorizer_computes_cosine_similarity(self) -> None:
        corpus = [
            ("p1", "VO2max training cardiac stroke volume", "Left ventricle end diastolic volume increases stroke volume."),
            ("p2", "FTP threshold progression", "Extend time in zone to raise threshold."),
        ]
        vectorizer = SemanticVectorizer()
        vectorizer.fit(corpus)

        scores = vectorizer.query("cardiac stroke volume heart remodeling", top_k=2)
        self.assertTrue(len(scores) >= 1)
        self.assertEqual(scores[0][0], "p1")


if __name__ == "__main__":
    unittest.main()
