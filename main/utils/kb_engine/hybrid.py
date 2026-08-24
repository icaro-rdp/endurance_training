"""
Hybrid Search & Reciprocal Rank Fusion for Endurance Training KB.
Combines sparse lexical BM25 rankings with dense vector / semantic representations.
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from collections.abc import Sequence
from typing import TYPE_CHECKING

from .models import EvidencePassage, EvidenceSearchResult

if TYPE_CHECKING:
    from .fts import PassageIndex


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

    for w, ranked_list in zip(weights, ranking_lists):
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
            dense_score=(
                round(dense_scores[cid], 8) if cid in dense_scores else None
            ),
            hybrid_score=round(rrf_scores[cid], 8),
        )
        for cid in sorted_chunk_ids[:limit]
    )


def search_hybrid(
    index: PassageIndex,
    query: str,
    category: str | None = None,
    topic: str | None = None,
    source_slug: str | None = None,
    limit: int = 5,
    candidate_k: int = 20,
    rrf_k: int = 60,
    dense_weight: float = 1.0,
    sparse_weight: float = 1.0,
    min_rrf_score: float = 0.012,
    min_dense_similarity: float = 0.65,
) -> tuple[EvidenceSearchResult, ...]:
    """Perform local hybrid retrieval fusing BM25 lexical and neural dense vectors.

    Applies calibrated internal score thresholds to reject unsupported-domain queries.
    """
    sparse_results = index.search_bm25(
        query=query,
        category=category,
        topic=topic,
        source_slug=source_slug,
        limit=candidate_k,
    )
    dense_results = index.search_dense(
        query=query,
        category=category,
        topic=topic,
        source_slug=source_slug,
        limit=candidate_k,
    )

    if not sparse_results and not dense_results:
        return ()

    # Threshold gating for unsupported-domain negative queries:
    # If no BM25 matches exist and top dense similarity is below threshold, reject as insufficient evidence
    if not sparse_results and dense_results:
        top_dense = dense_results[0]
        if (
            top_dense.dense_score is not None
            and top_dense.dense_score < min_dense_similarity
        ):
            return ()

    fused = reciprocal_rank_fusion(
        [sparse_results, dense_results],
        k=rrf_k,
        limit=limit,
        weights=[sparse_weight, dense_weight],
    )

    # If best fused score is below threshold, reject
    if fused and (fused[0].hybrid_score or 0.0) < min_rrf_score:
        return ()

    return fused


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
