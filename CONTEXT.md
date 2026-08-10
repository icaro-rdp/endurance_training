# Endurance Training Domain Context & Architecture Glossary

This document records the ubiquitous language, core domain concepts, and architectural vocabulary for this repository.

---

## Domain Concepts

- **Knowledge Base (KB)**: The curated collection of Markdown research articles, podcast episode notes, and reference books stored under `Knowledge_base/`.
- **Frontmatter**: Standardized YAML header metadata (`title`, `category`, `topics`, `summary`, `source`, `date`) embedded at the top of every KB document.
- **Taxonomy**: Canonical list of Categories (`metrics`, `hiit`, `zone2`, `strength`, `nutrition`, `physiology`, `periodization`, `book`) and Topics defined in `Knowledge_base/TAXONOMY.md`.
- **Sitemap / Index**: Master document catalog located at `Knowledge_base/INDEX.md` generated dynamically from document frontmatters.
- **Athlete Query**: A natural-language question about endurance-training concepts, decisions, or planning needs.
- **Semantic Retrieval**: Finding and ranking Evidence Passages by the meaning and training concepts expressed in an Athlete Query, including relevant passages that do not repeat its exact wording or use the same language. English and Italian queries and sources are part of the same retrieval space.
- **Diversified Retrieval**: Semantic Retrieval that balances relevance with coverage across distinct training concepts and Knowledge Sources for broad Athlete Queries.
- **Focused Retrieval**: Semantic Retrieval that prioritizes the strongest-matching passages within an optionally constrained source or topic for deep investigation.
- **Evidence Passage**: A bounded excerpt from a Knowledge Source with its document identity, author, language, source type, section hierarchy, stable location, and enough surrounding context to cite and inspect it accurately. Competing passages remain independently attributable when sources disagree.
- **Grounded Synthesis**: An explanation, comparison, or plan produced by a connected LLM from retrieved Evidence Passages, with source claims traceable to citations and inference kept distinguishable from source evidence.
- **Knowledge Source**: A curated article, podcast note, or book included in the Knowledge Base.
- **Corpus Synchronization**: The explicit operation that rebuilds all Derived Indexes from the current Knowledge Sources, including additions, edits, renames, and deletions.
- **Derived Index**: A reproducible local search artifact generated from Knowledge Sources. It is not a Knowledge Source and is invalid once the corpus changes.

---

## Architectural Seams & Modules

- **`KBEngine` (Deep Module)**: Core Python module located at `main/utils/kb_engine/` exposing `KBEngine` facade (`search()`, `build_index()`, `validate()`, `standardize()`). Encapsulates:
  - `retrieval.py`: Local hybrid retrieval engine executing SQLite FTS5 BM25 + `intfloat/multilingual-e5-base` 768-dim dense vectors with `sqlite-vec`, fused via Reciprocal Rank Fusion (RRF $k=60$) and reranked using `BAAI/bge-reranker-base` cross-encoder.
  - `chunker.py`: Structure-aware, citation-stable passage chunker (`StructureAwareChunker`) generating bounded excerpts with exact line ranges (`#L45-L89`), section hierarchy breadcrumbs, and deterministic chunk hashes.
  - `frontmatter.py`: Frontmatter parsing, standardization, YAML schema rules, and `key_takeaways` validation.
  - `validator.py`: Link verification, taxonomy checks, and sitemap integrity.
  - `sync.py`: Corpus SHA-256 state tracking and fail-fast `stale_index` verification.
- **MCP Adapter (`main/mcp_server.py`)**: `FastMCP` server exposing 4 specialized stdio tools (`search_evidence`, `get_passage`, `get_document`, `get_kb_status`) with path containment isolation and structured `isError: true` domain error handling.
- **CLI Adapters**: Thin command-line wrappers (`cli.py`, `build_index.py`, `validate_kb.py`) that delegate execution directly to `KBEngine`.

