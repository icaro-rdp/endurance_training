# Endurance Training Domain Context & Architecture Glossary

This document records the ubiquitous language, core domain concepts, and active architectural vocabulary for this repository.

---

## Domain Concepts

- **Knowledge Base (KB)**: The curated collection of English Markdown research articles, podcast episode notes, and reference books stored under `Knowledge_base/`.
- **Frontmatter**: YAML source metadata governed by the single canonical contract in `Knowledge_base/TAXONOMY.md`. The current validator requires `title`, `category`, `topics`, and `summary`; new Knowledge Sources additionally require English and provenance fields. `key_takeaways` is optional and included only when deliberately curated. Reviewed legacy sources without `language` are interpreted as English.
- **Taxonomy**: Canonical list of Categories (`metrics`, `hiit`, `zone2`, `strength`, `nutrition`, `physiology`, `periodization`, `book`) and Topics defined in `Knowledge_base/TAXONOMY.md`.
- **Sitemap / Index**: Master document catalog located at `Knowledge_base/INDEX.md` and generated from document frontmatter.
- **Athlete Query**: An English natural-language question about endurance-training concepts, decisions, or planning needs. Callers supply English; the retrieval foundation does not perform language identification.
- **Passage Retrieval**: Finding and ranking Evidence Passages with SQLite FTS5 BM25 lexical search. The active baseline can match English terms present in passage text, titles, and indexed metadata; semantic retrieval is not yet part of the product.
- **Focused Retrieval**: Passage Retrieval constrained by an optional category, topic, or Knowledge Source slug.
- **Evidence Passage**: A bounded excerpt from one Knowledge Source with document identity, author, English language metadata, source type, section hierarchy, stable location, and enough surrounding context to cite and inspect it accurately. Competing passages remain independently attributable when sources disagree.
- **Grounded Synthesis**: An explanation, comparison, or plan produced by a connected LLM from retrieved Evidence Passages, with source claims traceable to citations and inference kept distinguishable from source evidence.
- **Knowledge Source**: A curated English article, podcast note, or book included in the Knowledge Base.
- **Corpus Synchronization**: The explicit `build-index` operation that transactionally rebuilds the Derived Index from current Knowledge Sources. It covers additions, content edits, renames, and deletions; retrieval never synchronizes implicitly.
- **Corpus Fingerprint**: A deterministic SHA-256 digest over sorted Knowledge Source relative paths and content hashes, plus `TAXONOMY.md`. It is the freshness identity stored in the Derived Index.
- **Derived Index**: The reproducible local SQLite search artifact at `main/.kb_index.sqlite`. It is not a Knowledge Source, is Git-ignored, and is invalid once its Corpus Fingerprint differs from the current corpus.

---

## Architectural Seams & Modules

- **`KBEngine` (Deep Module)**: Core Python facade in `main/utils/kb_engine/`, exposing `search()`, `build_index()`, `get_passage()`, `get_kb_status()`, `validate()`, and `standardize()`.
  - `chunker.py`: `StructureAwareChunker`, which creates English, citation-stable Evidence Passages with bounded word-count policy, section breadcrumbs, exact source line ranges, stable content-derived IDs, and explicit size exceptions for indivisible blocks.
  - `fts.py`: `PassageIndex`, which owns the transactional SQLite schema (`meta`, `sources`, `passages`, `passages_fts`), performs BM25 lexical retrieval, and fails fast for missing, stale, or invalid indexes.
  - `sync.py`: Deterministic content-based Corpus Fingerprint construction.
  - `models.py` and `errors.py`: Evidence Passage, search-result, index-status, and domain-error contracts.
  - `frontmatter.py`: Frontmatter parsing and standardization.
  - `validator.py`: YAML and English-metadata checks, link verification,
    category/topic taxonomy warnings, targeted source diagnostics, and sitemap
    integrity. Ambiguous taxonomy corrections remain a contributor review
    responsibility.
- **MCP Server (`main/mcp_server.py`)**: Official MCP Python SDK stdio server (`endurance-kb-mcp`) exposing `search_passages`, `get_passage`, `get_document` (with strict path containment), `get_kb_status`, `get_taxonomy`, and `get_sitemap` for connected LLM retrieval and Grounded Synthesis.
- **CLI Adapter (`main/cli.py`)**: Thin command-line interface for explicit index synchronization, freshness status, English lexical search, validation, and frontmatter maintenance.

## Deferred Retrieval Work

Dense embeddings, vector search, score fusion, reranking, and result diversification are intentionally deferred. They require an executable English retrieval benchmark that demonstrates a measurable improvement over the FTS5 baseline. The active index build and query paths do not download model weights or require network access.
