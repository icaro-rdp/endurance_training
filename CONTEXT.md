# Endurance Training Domain Context & Architecture Glossary

This document records the ubiquitous language, core domain concepts, and architectural vocabulary for this repository.

---

## Domain Concepts

- **Knowledge Base (KB)**: The curated collection of Markdown research articles, podcast episode notes, and reference books stored under `Knowledge_base/`.
- **Frontmatter**: Standardized YAML header metadata (`title`, `category`, `topics`, `summary`, `source`, `date`) embedded at the top of every KB document.
- **Taxonomy**: Canonical list of Categories (`metrics`, `hiit`, `zone2`, `strength`, `nutrition`, `physiology`, `periodization`, `book`) and Topics defined in `Knowledge_base/TAXONOMY.md`.
- **Sitemap / Index**: Master document catalog located at `Knowledge_base/INDEX.md` generated dynamically from document frontmatters.

---

## Architectural Seams & Modules

- **`KBEngine` (Deep Module)**: Core Python module located at `main/kb_engine/` exposing `KBEngine` facade (`search()`, `build_index()`, `validate()`, `standardize()`). Encapsulates:
  - `fts.py`: SQLite FTS5 database setup & BM25 query handling with automatic timestamp-based cache invalidation.
  - `frontmatter.py`: Frontmatter parsing, standardization, and YAML schema rules.
  - `validator.py`: Link verification, taxonomy checks, and sitemap integrity.
- **CLI Adapters**: Thin command-line wrappers (`kb_search.py`, `build_index.py`, `validate_kb.py`, `standardize_frontmatter.py`, `mcp_server.py`) that delegate execution directly to `KBEngine`.
