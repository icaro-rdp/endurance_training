# 1. Local English Passage Retrieval Foundation & MCP Direction

- **Status**: Accepted, amended for the first implementation increment
- **Date**: 2026-08-10
- **Amended**: 2026-08-20
- **Deciders**: `icaro-rdp` & Antigravity Agent
- **Consulted Sub-issues**: GitHub Issues #2, #3, #4, #5, #6, #7, #8

---

## Context & Problem Statement

The Endurance Training Knowledge Base needs a private, offline-capable, local-first search foundation that turns curated English Markdown into citation-stable Evidence Passages for CLI and connected-LLM use.

The previous index split documents only at Markdown headings, rebuilt itself during queries, and used modification times as a freshness proxy. Flat converted books therefore became extremely large passages, citations drifted after frontmatter, and deletions or renamed sources could escape stale-index detection.

The first implementation increment must establish trustworthy passage ingestion and synchronization before semantic retrieval or a final MCP surface is attempted.

---

## Decision Drivers

- **English-Only Contract**: Active indexing accepts English Knowledge Sources only. Retrieval supports and benchmarks English Athlete Queries; identifying query language is a caller-side precondition rather than an indexing dependency.
- **Citation Provenance**: Every Evidence Passage carries its Knowledge Source identity, section hierarchy, and exact starting and ending source lines (`#L45-L89`).
- **Offline Operation**: Index construction and retrieval require no network access or model-weight download.
- **Low Operational Complexity**: One transactional SQLite file, with no background service or external vector database.
- **Strict Stale-Index Safety**: Retrieval fails clearly when Knowledge Source paths or contents differ from the explicitly synchronized corpus.
- **Evidence Before Complexity**: Dense retrieval, reranking, and diversification are adopted only after an executable English benchmark shows value over the lexical baseline.

---

## Decision Outcome

### 1. English Structure-Aware Evidence Passages

- `StructureAwareChunker` parses frontmatter, standard Markdown headings, supported English weak-heading markers, paragraphs, tables, blockquotes, and code fences.
- The default sizing policy targets 350 words, normally keeps passages between 80 and 600 words, and records explicit size status for an undersized section or an indivisible oversized block.
- Each passage includes a source slug and relative path, title, author, `language: en`, source type, category, topics, section hierarchy, exact line range, content, citation link, and a stable content-derived chunk ID.
- A Knowledge Source declaring a non-English language fails synchronization with `unsupported_language`.

### 2. SQLite FTS5 Baseline

- The active retriever is SQLite FTS5 BM25 over passage content, Knowledge Source titles, and indexed metadata.
- Search returns structured Evidence Passages plus a lexical score and supports exact category, topic, and source-slug filters.
- Queries never rebuild the index implicitly. Missing, stale, and invalid indexes produce distinct domain errors with instructions to run `endurance-kb build-index`.
- This baseline is lexical passage retrieval, not hybrid or semantic retrieval.

### 3. Single Local Derived Index

- The canonical Derived Index is `main/.kb_index.sqlite`, which is Git-ignored and reproducible.
- Its schema contains `sources`, `passages`, `passages_fts`, and `meta` tables.
- Synchronization builds a temporary database, validates the full operation, and atomically replaces the previous index only after success.

### 4. Content-Fingerprint Synchronization

- Corpus Synchronization computes a deterministic SHA-256 fingerprint from sorted Knowledge Source relative paths and their content hashes, plus `TAXONOMY.md`.
- The fingerprint detects additions, content edits, renames, deletions, and taxonomy changes without relying on filesystem modification times.
- `status` compares the current and indexed fingerprints. Search and passage lookup fail fast with `stale_index` when they differ.

### 5. MCP Server Contract

The responsibility boundary remains: the Knowledge Base retrieves citation-quality Evidence Passages, while a connected LLM performs Grounded Synthesis. The MCP server (`main/mcp_server.py`, command `endurance-kb-mcp`) implements the official MCP Python SDK with stdio transport, exposes passage retrieval tools (`search_passages`, `get_passage`, `get_document`, `get_kb_status`, `get_taxonomy`, `get_sitemap`), enforces strict path containment against directory traversal, and maps domain errors to actionable diagnostics.

### 6. Benchmark-Gated Semantic Retrieval

Dense embeddings, vector storage, fusion, reranking, and diversified ranking remain undecided implementation work. Before selecting any model or backend, the repository must provide an executable English benchmark with valid passage-level gold targets, baseline metrics, latency reporting, and negative-query evaluation. A later ADR amendment will record any adopted stack.

---

## Positive Consequences

- Indexing and retrieval work offline without model downloads or external services.
- Exact line ranges and stable passage identities make evidence inspectable and citeable.
- Content-based freshness catches corpus changes that modification-time checks miss.
- Transactional replacement preserves the last complete index when synchronization fails.
- The lexical baseline provides a reproducible comparison point for later retrieval experiments.

---

## Negative Consequences & Mitigation

- **Lexical Recall Limits**: FTS5 may miss synonyms or conceptually related passages that do not share query terms.
  - *Mitigation*: Measure this limitation with the executable English benchmark before adding semantic complexity.
- **English-Only Scope**: Non-English sources and queries are outside the active product contract.
  - *Mitigation*: Reconsider language scope only through a separate benchmark and decision.
- **Deferred MCP Hardening**: The legacy MCP adapter does not yet implement the final evidence contract.
  - *Mitigation*: Treat MCP modernization as a separate increment after the core retrieval API stabilizes.
