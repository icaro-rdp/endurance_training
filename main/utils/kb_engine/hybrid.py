"""
Hybrid Search & Reciprocal Rank Fusion for Endurance Training KB.
Combines sparse lexical BM25 rankings with dense vector / semantic representations.
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .models import EvidencePassage, EvidenceSearchResult

if TYPE_CHECKING:
    from .fts import PassageIndex


@dataclass(frozen=True, slots=True)
class EvidenceSelectionPolicy:
    """Bounded, server-side policy for retaining useful Evidence Passages.

    The values are deliberately centralised so the benchmark can calibrate them
    later. MCP clients never receive or tune ranking scores.
    """

    candidate_limit: int = 20
    maximum_passages: int = 20
    minimum_hybrid_score: float = 0.020
    hybrid_score_ratio: float = 0.75
    minimum_dense_similarity: float = 0.65
    dense_similarity_drop: float = 0.05

    def __post_init__(self) -> None:
        if not 1 <= self.maximum_passages <= self.candidate_limit:
            raise ValueError("maximum_passages must be within the candidate limit")
        if not 0.0 < self.hybrid_score_ratio <= 1.0:
            raise ValueError("hybrid_score_ratio must be in (0, 1]")
        if not 0.0 <= self.minimum_dense_similarity <= 1.0:
            raise ValueError("minimum_dense_similarity must be in [0, 1]")
        if self.dense_similarity_drop < 0.0:
            raise ValueError("dense_similarity_drop must be non-negative")


DEFAULT_EVIDENCE_SELECTION_POLICY = EvidenceSelectionPolicy()


def reciprocal_rank_fusion(
    ranking_lists: Sequence[Sequence[EvidenceSearchResult]],
    k: int = 60,
    limit: int = 5,
    weights: Sequence[float] | None = None,
) -> tuple[EvidenceSearchResult, ...]:
    """Fuse multiple ranked result lists using Reciprocal Rank Fusion (RRF).

    Formula:
        RRF_Score(d) = sum_{m in rankings} (w_m / (k + rank_m(d)))
    """
    if not ranking_lists:
        return ()

    if weights is None:
        weights = [1.0] * len(ranking_lists)

    rrf_scores: dict[str, float] = defaultdict(float)
    dense_scores: dict[str, float] = {}
    lexical_scores: dict[str, float] = {}
    passage_map: dict[str, EvidencePassage] = {}

    for w, ranked_list in zip(weights, ranking_lists, strict=True):
        for rank, result in enumerate(ranked_list, start=1):
            passage = result.passage
            chunk_id = passage.chunk_id
            rrf_scores[chunk_id] += w / (k + rank)
            if result.dense_score is not None:
                dense_scores[chunk_id] = max(
                    dense_scores.get(chunk_id, 0.0), result.dense_score
                )
            if result.lexical_score != 0.0:
                lexical_scores[chunk_id] = max(
                    lexical_scores.get(chunk_id, 0.0), result.lexical_score
                )
            if chunk_id not in passage_map:
                passage_map[chunk_id] = passage

    sorted_chunk_ids = sorted(
        rrf_scores.keys(),
        key=lambda cid: rrf_scores[cid],
        reverse=True,
    )

    return tuple(
        EvidenceSearchResult(
            passage=passage_map[cid],
            lexical_score=round(lexical_scores.get(cid, 0.0), 8),
            dense_score=(round(dense_scores[cid], 8) if cid in dense_scores else None),
            hybrid_score=round(rrf_scores[cid], 8),
        )
        for cid in sorted_chunk_ids[:limit]
    )


def select_relevant_passages(
    candidates: Sequence[EvidenceSearchResult],
    policy: EvidenceSelectionPolicy = DEFAULT_EVIDENCE_SELECTION_POLICY,
) -> tuple[EvidenceSearchResult, ...]:
    """Keep the useful head of a fused candidate list without filling a quota.

    A retained passage needs support from both retrievers (RRF score) or must be
    close to the strongest local dense match. This preserves strong semantic
    matches while removing the weak tail.
    """
    if not candidates:
        return ()

    bounded = tuple(candidates[: policy.candidate_limit])
    top_hybrid_score = max(
        (result.hybrid_score or 0.0 for result in bounded), default=0.0
    )
    top_dense_score = max(
        (result.dense_score for result in bounded if result.dense_score is not None),
        default=None,
    )
    hybrid_floor = max(
        policy.minimum_hybrid_score,
        top_hybrid_score * policy.hybrid_score_ratio,
    )
    dense_floor = (
        max(
            policy.minimum_dense_similarity,
            top_dense_score - policy.dense_similarity_drop,
        )
        if top_dense_score is not None
        else None
    )

    retained = [
        result
        for result in bounded
        if (result.hybrid_score or 0.0) >= hybrid_floor
        or (
            dense_floor is not None
            and result.dense_score is not None
            and result.dense_score >= dense_floor
        )
    ]
    return tuple(retained[: policy.maximum_passages])


def search_hybrid(
    index: PassageIndex,
    query: str,
    category: str | None = None,
    topic: str | None = None,
    source_slug: str | None = None,
    limit: int = DEFAULT_EVIDENCE_SELECTION_POLICY.maximum_passages,
    policy: EvidenceSelectionPolicy = DEFAULT_EVIDENCE_SELECTION_POLICY,
    rrf_k: int = 60,
    dense_weight: float = 1.0,
    sparse_weight: float = 1.0,
    retain_evidence: bool = True,
) -> tuple[EvidenceSearchResult, ...]:
    """Perform local hybrid retrieval fusing BM25 lexical and neural dense vectors.

    Explores a bounded candidate pool, then normally applies the server-side
    evidence selection policy before returning retained passages.
    """
    sparse_results = index.search_bm25(
        query=query,
        category=category,
        topic=topic,
        source_slug=source_slug,
        limit=policy.candidate_limit,
    )
    dense_results = index.search_dense(
        query=query,
        category=category,
        topic=topic,
        source_slug=source_slug,
        limit=policy.candidate_limit,
    )

    if not sparse_results and not dense_results:
        return ()

    fused = reciprocal_rank_fusion(
        [sparse_results, dense_results],
        k=rrf_k,
        limit=policy.candidate_limit,
        weights=[sparse_weight, dense_weight],
    )
    if not retain_evidence:
        return fused
    retained = select_relevant_passages(fused, policy=policy)
    return retained[: min(limit, policy.maximum_passages)]


class SemanticVectorizer:
    """Lightweight, pure-Python semantic vectorizer with sub-word n-grams and TF-IDF."""

    def __init__(self, ngram_range: tuple[int, int] = (3, 5)) -> None:
        self.ngram_range = ngram_range
        self.doc_count = 0
        self.idf: dict[str, float] = {}
        self.doc_vectors: dict[str, dict[str, float]] = {}

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        words = re.findall(r"\w+", text.lower())
        return [w for w in words if len(w) > 1]

    def _extract_features(self, text: str) -> dict[str, float]:
        features: dict[str, float] = defaultdict(float)
        words = self._tokenize(text)
        # Word unigrams
        for word in words:
            features[word] += 1.0
            # Character n-grams for subword / morphology matching
            min_n, max_n = self.ngram_range
            for n in range(min_n, min(len(word) + 1, max_n + 1)):
                for i in range(len(word) - n + 1):
                    ngram = word[i : i + n]
                    features[f"ng:{ngram}"] += 0.5
        return dict(features)

    def fit(self, documents: Sequence[tuple[str, str, str]]) -> None:
        """Fit vectorizer on (doc_id, title_and_metadata, content) tuples."""
        self.doc_count = len(documents)
        df: Counter[str] = Counter()
        raw_features: dict[str, dict[str, float]] = {}

        for doc_id, meta, content in documents:
            combined_text = f"{meta} {meta} {content}"
            feats = self._extract_features(combined_text)
            raw_features[doc_id] = feats
            for term in feats:
                df[term] += 1

        # Compute smoothed IDF
        self.idf = {
            term: math.log((self.doc_count + 1.0) / (count + 1.0)) + 1.0
            for term, count in df.items()
        }

        # Build L2-normalized doc vectors
        self.doc_vectors = {}
        for doc_id, feats in raw_features.items():
            vec: dict[str, float] = {}
            for term, tf in feats.items():
                idf_val = self.idf.get(term, 1.0)
                vec[term] = (1.0 + math.log(tf)) * idf_val

            norm = math.sqrt(sum(v * v for v in vec.values()))
            if norm > 0:
                self.doc_vectors[doc_id] = {k: v / norm for k, v in vec.items()}
            else:
                self.doc_vectors[doc_id] = vec

    def query(self, query_text: str, top_k: int = 20) -> list[tuple[str, float]]:
        """Query vector index and return top_k (doc_id, cosine_score) pairs."""
        query_feats = self._extract_features(query_text)
        if not query_feats:
            return []

        q_vec: dict[str, float] = {}
        for term, tf in query_feats.items():
            if term in self.idf:
                q_vec[term] = (1.0 + math.log(tf)) * self.idf[term]

        q_norm = math.sqrt(sum(v * v for v in q_vec.values()))
        if q_norm <= 0:
            return []
        q_vec = {k: v / q_norm for k, v in q_vec.items()}

        scores: list[tuple[str, float]] = []
        for doc_id, d_vec in self.doc_vectors.items():
            dot = sum(val * d_vec.get(term, 0.0) for term, val in q_vec.items())
            if dot > 0.0:
                scores.append((doc_id, dot))

        scores.sort(key=lambda item: item[1], reverse=True)
        return scores[:top_k]
