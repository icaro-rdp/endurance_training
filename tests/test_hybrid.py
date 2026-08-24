"""Unit tests for Hybrid Search & Reciprocal Rank Fusion."""

from __future__ import annotations

import unittest

from main.utils.kb_engine.hybrid import (
    EvidenceSelectionPolicy,
    SemanticVectorizer,
    reciprocal_rank_fusion,
    select_relevant_passages,
)
from main.utils.kb_engine.models import (
    EvidencePassage,
    EvidenceSearchResult,
    PassageSizeStatus,
)


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
        # p2 appears in both rankings, so its fused score is highest.
        self.assertEqual(fused[0].passage.chunk_id, "c2")
        self.assertEqual(fused[1].passage.chunk_id, "c1")
        self.assertEqual(fused[2].passage.chunk_id, "c3")

    def test_selection_keeps_all_twenty_consistently_high_candidates(self) -> None:
        ranking = [
            EvidenceSearchResult(
                _dummy_passage(f"c{index}", f"Passage {index}", "Content"),
                lexical_score=float(21 - index),
            )
            for index in range(1, 21)
        ]

        fused = reciprocal_rank_fusion([ranking, ranking], k=60, limit=20)
        retained = select_relevant_passages(fused)

        self.assertEqual(len(retained), 20)

    def test_selection_removes_weak_tail_after_score_drop(self) -> None:
        p1 = _dummy_passage("strong-1", "Strong one", "Content")
        p2 = _dummy_passage("strong-2", "Strong two", "Content")
        p3 = _dummy_passage("weak", "Weak", "Content")
        candidates = (
            EvidenceSearchResult(p1, 10.0, dense_score=0.80, hybrid_score=0.030),
            EvidenceSearchResult(p2, 8.0, dense_score=0.76, hybrid_score=0.027),
            EvidenceSearchResult(p3, 0.0, dense_score=0.68, hybrid_score=0.013),
        )

        retained = select_relevant_passages(
            candidates,
            policy=EvidenceSelectionPolicy(maximum_passages=20),
        )

        self.assertEqual(
            [item.passage.chunk_id for item in retained], ["strong-1", "strong-2"]
        )

    def test_selection_returns_no_evidence_when_every_candidate_is_weak(self) -> None:
        candidate = EvidenceSearchResult(
            _dummy_passage("weak", "Weak", "Content"),
            0.0,
            dense_score=0.64,
            hybrid_score=0.014,
        )

        self.assertEqual(select_relevant_passages([candidate]), ())

    def test_semantic_vectorizer_computes_cosine_similarity(self) -> None:
        corpus = [
            (
                "p1",
                "VO2max training cardiac stroke volume",
                "Left ventricle end diastolic volume increases stroke volume.",
            ),
            (
                "p2",
                "FTP threshold progression",
                "Extend time in zone to raise threshold.",
            ),
        ]
        vectorizer = SemanticVectorizer()
        vectorizer.fit(corpus)

        scores = vectorizer.query("cardiac stroke volume heart remodeling", top_k=2)
        self.assertTrue(len(scores) >= 1)
        self.assertEqual(scores[0][0], "p1")


if __name__ == "__main__":
    unittest.main()
