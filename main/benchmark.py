#!/usr/bin/env python3
"""
Executable benchmark runner for the English Endurance Training Retrieval Benchmark.
Evaluates MRR@5, NDCG@5, Recall@5, latency, and negative queries against
docs/prototypes/003-retrieval-benchmark.json.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from main.utils.kb_engine import KBEngine

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BENCHMARK_PATH = (
    PROJECT_ROOT / "docs" / "prototypes" / "003-retrieval-benchmark.json"
)


@dataclass(frozen=True)
class QueryMetrics:
    query_id: str
    query_text: str
    category: str
    mrr_at_5: float
    ndcg_at_5: float
    recall_at_5: float
    retrieved_count: int
    gold_count: int
    matched_gold_titles: list[str]
    latency_ms: float


def compute_dcg(relevances: list[int], k: int = 5) -> float:
    dcg = 0.0
    for i, rel in enumerate(relevances[:k], start=1):
        if rel > 0:
            dcg += (math.pow(2, rel) - 1) / math.log2(i + 1)
    return dcg


def compute_ndcg(retrieved_relevances: list[int], ideal_relevances: list[int], k: int = 5) -> float:
    dcg = compute_dcg(retrieved_relevances, k=k)
    idcg = compute_dcg(sorted(ideal_relevances, reverse=True), k=k)
    if idcg <= 0.0:
        return 0.0
    return dcg / idcg


def evaluate_benchmark(
    engine: KBEngine,
    benchmark_path: Path = DEFAULT_BENCHMARK_PATH,
    top_k: int = 5,
) -> dict[str, object]:
    data = json.loads(benchmark_path.read_text(encoding="utf-8"))
    queries = data["queries"]

    positive_results: list[QueryMetrics] = []
    negative_results: list[dict[str, object]] = []

    # Warmup query
    engine.search("warmup query", top_k=1)

    for q in queries:
        qid = q["id"]
        q_text = q["query"]
        category = q["category"]
        gold_passages = q.get("gold_passages", [])

        start_time = time.perf_counter()
        results = engine.search(q_text, top_k=top_k)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if not gold_passages:
            # Negative query
            negative_results.append({
                "id": qid,
                "query": q_text,
                "category": category,
                "retrieved_count": len(results),
                "top_score": results[0].lexical_score if results else 0.0,
                "latency_ms": elapsed_ms,
            })
            continue

        # Positive query evaluation
        # Map gold passages by (rel_path, start_line, end_line) or title / line overlap
        gold_targets = [
            (
                g["rel_path"],
                int(g["start_line"]),
                int(g["end_line"]),
                int(g["relevance_score"]),
                g["title"],
            )
            for g in gold_passages
        ]

        retrieved_relevances: list[int] = []
        matched_titles: list[str] = []
        first_match_rank: int | None = None

        for rank, res in enumerate(results[:top_k], start=1):
            passage = res.passage
            matched_rel = 0
            for g_path, g_start, g_end, g_score, g_title in gold_targets:
                if passage.rel_path == g_path and passage.start_line == g_start and passage.end_line == g_end:
                    matched_rel = g_score
                    if g_title not in matched_titles:
                        matched_titles.append(g_title)
                    break
                # Relaxed match: same source and substantial line overlap
                elif (
                    passage.rel_path == g_path
                    and not (passage.end_line < g_start or passage.start_line > g_end)
                ):
                    matched_rel = g_score
                    if g_title not in matched_titles:
                        matched_titles.append(g_title)
                    break

            retrieved_relevances.append(matched_rel)
            if matched_rel > 0 and first_match_rank is None:
                first_match_rank = rank

        ideal_relevances = [g[3] for g in gold_targets]
        mrr = 1.0 / first_match_rank if first_match_rank else 0.0
        ndcg = compute_ndcg(retrieved_relevances, ideal_relevances, k=top_k)
        recall = len(matched_titles) / len(gold_targets) if gold_targets else 0.0

        positive_results.append(
            QueryMetrics(
                query_id=qid,
                query_text=q_text,
                category=category,
                mrr_at_5=mrr,
                ndcg_at_5=ndcg,
                recall_at_5=recall,
                retrieved_count=len(results),
                gold_count=len(gold_targets),
                matched_gold_titles=matched_titles,
                latency_ms=elapsed_ms,
            )
        )

    # Compute aggregate metrics
    num_pos = len(positive_results)
    mean_mrr = sum(r.mrr_at_5 for r in positive_results) / num_pos if num_pos else 0.0
    mean_ndcg = sum(r.ndcg_at_5 for r in positive_results) / num_pos if num_pos else 0.0
    mean_recall = sum(r.recall_at_5 for r in positive_results) / num_pos if num_pos else 0.0
    latencies = sorted(r.latency_ms for r in positive_results)
    p95_idx = int(math.ceil(0.95 * len(latencies))) - 1 if latencies else 0
    p95_latency = latencies[p95_idx] if latencies else 0.0

    return {
        "summary": {
            "positive_query_count": num_pos,
            "mean_mrr_at_5": round(mean_mrr, 4),
            "mean_ndcg_at_5": round(mean_ndcg, 4),
            "mean_recall_at_5": round(mean_recall, 4),
            "latency_p95_ms": round(p95_latency, 2),
            "negative_query_count": len(negative_results),
        },
        "positive_queries": [
            {
                "id": r.query_id,
                "category": r.category,
                "query": r.query_text,
                "mrr_at_5": round(r.mrr_at_5, 4),
                "ndcg_at_5": round(r.ndcg_at_5, 4),
                "recall_at_5": round(r.recall_at_5, 4),
                "latency_ms": round(r.latency_ms, 2),
                "matched_golds": r.matched_gold_titles,
            }
            for r in positive_results
        ],
        "negative_queries": negative_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run English Retrieval Benchmark")
    parser.add_argument(
        "--json", action="store_true", help="Output results formatted as JSON"
    )
    parser.add_argument(
        "--top-k", type=int, default=5, help="Number of retrieved results (default: 5)"
    )
    args = parser.parse_args()

    engine = KBEngine()
    results = evaluate_benchmark(engine, top_k=args.top_k)

    if args.json:
        print(json.dumps(results, indent=2))
        return 0

    summary = cast(dict[str, Any], results["summary"])
    print("=" * 60)
    print("     English Endurance Training Retrieval Benchmark")
    print("=" * 60)
    print(f"Positive Queries: {summary['positive_query_count']}")
    print(f"Negative Queries: {summary['negative_query_count']}")
    print("-" * 60)
    print(f"Mean MRR@5:    {summary['mean_mrr_at_5']:.4f}  (Target: >= 0.8500)")
    print(f"Mean NDCG@5:   {summary['mean_ndcg_at_5']:.4f}  (Target: >= 0.8000)")
    print(f"Mean Recall@5: {summary['mean_recall_at_5']:.4f}  (Target: >= 0.8500)")
    print(f"Latency p95:   {summary['latency_p95_ms']:.2f} ms   (Target: < 500 ms)")
    print("=" * 60)
    print("\nPer-Query Performance:")
    positive_queries = cast(list[dict[str, Any]], results["positive_queries"])
    for pq in positive_queries:
        print(
            f"  [{pq['id']}] ({pq['category']}) MRR: {pq['mrr_at_5']:.2f} | "
            f"NDCG: {pq['ndcg_at_5']:.2f} | Recall: {pq['recall_at_5']:.2f} | "
            f"Matches: {len(pq['matched_golds'])}"
        )
        print(f"       Query: \"{pq['query']}\"")
        if pq["matched_golds"]:
            print(f"       Hits: {', '.join(pq['matched_golds'][:2])}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
