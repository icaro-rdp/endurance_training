# English Retrieval Foundation and Benchmark Reset

**Date:** 2026-08-20

**Status:** Current foundation; semantic model selection remains open

## Decision reset

The first implementation is English-only and lexical. The previous report presented embedding, reranker, vector-backend, memory, latency, and quality claims as benchmark results without a reproducible harness or retained result artifact. Those claims are withdrawn and are not an implementation contract.

No dense embedding model, reranker, fusion strategy, vector extension, or relevance threshold has been selected for the current corpus.

## Implemented baseline

The production foundation provides:

- structure-aware English Evidence Passages;
- a passage-level SQLite FTS5 index;
- BM25 lexical ranking with category, topic, and source filters;
- explicit, transactional Corpus Synchronization;
- a deterministic SHA-256 corpus manifest;
- fail-fast missing-index and stale-index errors;
- local operation with no model download or runtime network dependency.

This is the baseline against which later semantic retrieval must prove value.

## Benchmark status

The former prototype query set was removed because it included unsupported-language queries and targets that are no longer Knowledge Sources. A new suite must be created before retrieval acceptance is wired to CI.

A valid English benchmark must resolve gold evidence against production Evidence Passages and cover:

1. exact terminology and acronym queries;
2. English paraphrases and vocabulary mismatch;
3. focused queries with category, topic, and source filters;
4. broad queries that need evidence from distinct sources;
5. competing or qualifying evidence;
6. unsupported questions that should abstain.

Gold records should retain the source path and a unique target snippet as human-reviewable guards, then resolve to stable passage identifiers. Corpus changes that alter the evidence text must fail benchmark validation rather than silently relabeling it.

## Required measurements

Compare every future candidate with the FTS5 baseline using the same synchronized corpus and query set.

- MRR, NDCG, and recall at the selected result depth
- false-positive and abstention behavior on negative queries
- index duration and peak memory
- warm query latency and cold process/model startup measured separately
- index and model disk size
- clean-install burden on supported platforms
- offline behavior after any explicit provisioning step
- license and redistribution constraints

Report per-query results as well as aggregates. A small average improvement must not hide regressions on safety-critical negative cases or source-conflict queries.

## Candidate decision gate

Semantic components may be added only after a reproducible benchmark shows a material improvement over lexical retrieval.

The evaluation order should be incremental:

1. FTS5 BM25 baseline
2. one English dense retriever
3. lexical and dense fusion
4. optional reranking
5. optional diversification and calibrated abstention

Each stage must justify its additional dependency, memory, latency, and operational cost. If a reranker or vector extension does not improve the accepted benchmark, omit it.

Any later model or backend selection requires an ADR update based on retained commands, environment details, and machine-readable results.

## Implementation references

- `main/utils/kb_engine/chunker.py`
- `main/utils/kb_engine/fts.py`
- `main/utils/kb_engine/sync.py`
- `main/utils/kb_engine/models.py`
- `tests/test_chunker.py`
- `tests/test_passage_index.py`
