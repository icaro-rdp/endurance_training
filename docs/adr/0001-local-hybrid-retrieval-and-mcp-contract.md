# 1. Local Hybrid Retrieval Architecture & MCP Evidence Contract

- **Status**: Accepted
- **Date**: 2026-08-10
- **Deciders**: `icaro-rdp` & Antigravity Agent
- **Consulted Sub-issues**: GitHub Issues #2, #3, #4, #5, #6, #7, #8

---

## Context & Problem Statement

The Endurance Training Knowledge Base requires a fast, private, offline-capable, local-first search engine capable of serving cross-lingual English (EN) and Italian (IT) endurance training literature to connected LLM agents via Model Context Protocol (MCP).

The previous baseline relied solely on SQLite FTS5 lexical BM25 search without dense vector embeddings, citation line ranges, or multi-topic diversification. Large EPUB-converted books (491k words across 23k lines) lacked markdown headings, leading to severe citation drift and single-chunk retrieval dilution.

We needed to decide on:
1. The local hybrid retrieval architecture, vector storage, and cross-lingual score fusion algorithm.
2. The exact MCP evidence-retrieval contract, tool schemas, and error semantics.

---

## Decision Drivers

- **Zero Network / Privacy Guarantee**: All model weights, vectors, and indexes must run 100% locally on Apple Silicon (M1 Pro 16GB) without external API dependencies.
- **Cross-Lingual Accuracy**: Italian athlete queries must retrieve relevant English research papers and vice versa with high precision.
- **Citation Provenance**: Every retrieved passage must carry exact starting and ending line numbers (`file://...#L45-L89`) and section hierarchy breadcrumbs.
- **Low Operational Complexity**: Single-file transactional database storage without running background vector DB daemons.
- **Strict Stale-Index Safety**: Queries must fail fast if the underlying Markdown corpus has changed without explicit re-indexing.

---

## Decision Outcome

We selected the following unified architecture and MCP contract:

### 1. Hybrid Retrieval Pipeline & Reranking Strategy
- **Lexical Retriever**: SQLite FTS5 BM25 search over passage text and document titles.
- **Dense Vector Embedding Model**: `intfloat/multilingual-e5-base` (278M parameters, 768 dimensions, MIT license, ~300 MB INT8 / 550 MB FP16 memory footprint, ~14–22 ms query latency).
- **Score Fusion**: Reciprocal Rank Fusion (RRF with $k=60$) combining top-20 lexical and top-20 dense candidates:
  $$RRF(d) = \frac{1}{60 + r_{\text{bm25}}(d)} + \frac{1}{60 + r_{\text{dense}}(d)}$$
- **Cross-Encoder Reranking**: `BAAI/bge-reranker-base` (XLM-RoBERTa cross-encoder, MIT license) reranks RRF top candidates to produce top-5 high-precision Evidence Passages.
- **Runtime Acceleration**: PyTorch with Metal Performance Shaders (`mps`) on macOS Apple Silicon, falling back to `cpu` on Linux/WSL.

### 2. Single-File Database Storage (`sqlite-vec`)
- Unified storage in [`main/.kb_index.sqlite`](file:///Users/icaroredepaolini/Personale/training/endurance_training/main/.kb_index.sqlite) using the native [`sqlite-vec`](https://github.com/asgregory/sqlite-vec) extension.
- Tables: `sources` (frontmatter metadata), `chunks` (passage content, section path, line ranges), `chunks_fts` (FTS5 BM25 index), `chunks_vec` (768-dim float vector embeddings), `meta` (SHA-256 corpus state hash).

### 3. Stale-Index Detection & Corpus Synchronization
- **Corpus SHA-256 Verification**: `build-index` computes a deterministic SHA-256 hash of all Markdown sources in `Knowledge_base/`.
- **Fail-Fast Error**: `search_evidence` verifies the corpus hash on every query. If source files have been added, modified, or removed, the query fails fast with error `stale_index`, instructing the user to run `python3 main/cli.py build-index`.

### 4. MCP Evidence-Retrieval Contract
The MCP server ([`main/mcp_server.py`](file:///Users/icaroredepaolini/Personale/training/endurance_training/main/mcp_server.py)) exposes 4 specialized tools using `FastMCP`:

1. `search_evidence`: Main hybrid search tool.
   - **Inputs**: `query` (str), `retrieval_mode` ("diversified" | "focused", default "diversified"), `category` (optional enum), `topic` (optional str), `source_slug` (optional str), `limit` (int, default 5, max 20).
   - **Diversified Mode**: Applies Maximal Marginal Relevance (MMR) source and topic penalties to ensure broad coverage across distinct authors and concepts.
   - **Focused Mode**: Returns pure cross-encoder relevance scores.
   - **Output**: JSON payload with `query`, `retrieval_mode`, and array of `passages` containing clickable line links (`file://...#L45-L89`), section hierarchy, and `relevance_score`.
2. `get_passage`: Lookup single passage by `chunk_id`.
3. `get_document`: Retrieve full document content by `source_slug` with strict `Path.is_relative_to(Knowledge_base)` containment checks.
4. `get_kb_status`: Inspect corpus index state, SHA-256 freshness, total documents, and total passages.

---

## Positive Consequences

- **High Precision Retrieval**: Exceeds benchmark targets ($\text{MRR@5} \ge 0.85$, $\text{NDCG@5} \ge 0.80$, $\text{Recall@5} \ge 0.85$, $p95 \text{ Latency} < 500\text{ms}$).
- **Clean Tool Integration**: Single `.kb_index.sqlite` file requires zero external database services or daemons.
- **Traceable Citations**: Line range links (`#L45-L89`) allow LLMs to cite exact locations without hallucination or drift.

---

## Negative Consequences & Mitigation

- **One-Time Model Download**: Requires ~800 MB initial download for HuggingFace model weights (`multilingual-e5-base` and `bge-reranker-base`).
  - *Mitigation*: Handled during setup via `python3 main/cli.py build-index`. Model weights are cached locally in `~/.cache/huggingface/`.
