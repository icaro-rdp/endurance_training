# Endurance Training Knowledge Base

This repository contains a curated English endurance-training Knowledge Base and
a local, citation-oriented search tool. Markdown sources are split into
structure-aware Evidence Passages and indexed with SQLite FTS5 BM25. Search
results include the source path, section context, and exact line range.

The active retrieval foundation is deliberately simple:

- English sources and English queries only;
- explicit, transactional index builds;
- no network access or model downloads during indexing or search;
- no embeddings, reranker, or semantic-retrieval claims yet.

## Quick start

Prerequisites:

- Git;
- Python 3.10 or newer;
- `uv`;
- a Python SQLite build with FTS5 and JSON1 support.

```bash
git clone https://github.com/icaro-rdp/endurance_training.git
cd endurance_training
uv sync --locked
uv run endurance-kb build-index
uv run endurance-kb status
uv run endurance-kb search "VO2max cardiac hypertrophy preload"
```

`status` should report `"state": "fresh"` and `"is_fresh": true`.
The first `build-index` creates the ignored local database at
`main/.kb_index.sqlite` and regenerates `Knowledge_base/INDEX.md`.

Dependency installation may contact the configured package registry. Once the
locked environment is installed, building and searching the index are offline
operations.

## Repository map

- [`Knowledge_base/`](Knowledge_base/) — curated Markdown Knowledge Sources.
  - [`Articles/`](Knowledge_base/Articles/) — articles and research notes.
  - [`Episodes/`](Knowledge_base/Episodes/) — curated podcast notes.
  - [`Books/`](Knowledge_base/Books/) — book-derived reference material.
  - [`TAXONOMY.md`](Knowledge_base/TAXONOMY.md) — canonical categories, topics,
    and frontmatter guidance.
  - [`INDEX.md`](Knowledge_base/INDEX.md) — generated master sitemap.
- [`main/utils/kb_engine/`](main/utils/kb_engine/) — chunking, synchronization,
  validation, retrieval, and domain models.
- [`main/cli.py`](main/cli.py) — command-line adapter.
- [`tests/`](tests/) — unit, integration, and benchmark-integrity tests.
- [`CONTEXT.md`](CONTEXT.md) — domain vocabulary and architectural boundaries.
- [`docs/adr/`](docs/adr/) and [`docs/specs/`](docs/specs/) — decisions and
  implemented specifications.
- [`laTeX/training_plan.tex`](laTeX/training_plan.tex) — endurance training plan
  source; `laTeX/training_plan.pdf` is its generated output.

## Common commands

### Search

```bash
# LLM-ready excerpts with citations
uv run endurance-kb search "How should 4x8 minute VO2max intervals be structured?"

# Exact category and topic filters
uv run endurance-kb search "carbohydrate ratio" \
  --category nutrition --topic Carbohydrate_ratio

# Exact Knowledge Source slug: path relative to Knowledge_base, without .md
uv run endurance-kb search "threshold progression" \
  --source Episodes/Empirical_cycling_podcast/training/threshold/FTP_training

# One to twenty results in plain text or JSON
uv run endurance-kb search "FTP test protocol" --top 3 --format plain
uv run endurance-kb search "over-unders" --format json
```

Category, topic, and source filters are exact and case-sensitive. Query text
must be English. The retrieval layer does not identify or translate languages.

### Synchronize and inspect the index

```bash
uv run endurance-kb build-index
uv run endurance-kb status
```

Search never rebuilds the index. Adding, editing, renaming, or deleting a
Knowledge Source—or changing `Knowledge_base/TAXONOMY.md`—makes the current
index stale until `build-index` runs successfully.

### Validate source health

```bash
uv run endurance-kb validate
```

Validation errors are blocking. Warnings are advisory and can be numerous for
converted books with unresolved original links; inspect them, but do not assume
a zero exit code means there were no warnings.

### Standardize frontmatter

`standardize` writes files; it is not a preview command. Without `--force`, it
adds inferred frontmatter only to documents that have none. With `--force`, it
replaces existing frontmatter across the corpus. Prefer writing and reviewing
frontmatter manually for a new source.

```bash
uv run endurance-kb standardize
uv run endurance-kb standardize --force  # destructive bulk metadata rewrite
```

Do not run either command casually, especially `--force`.

## Testing changes

Install the locked development environment with `uv sync --locked`, then run:

```bash
PYTHONDONTWRITEBYTECODE=1 uv run python -m unittest discover -s tests -v
uv run ruff check main/cli.py main/utils/kb_engine tests
uv run ruff format --check main/cli.py main/utils/kb_engine tests
uv run mypy
git diff --check
```

The Ruff paths intentionally cover the active retrieval implementation and its
tests. Older conversion, scraper, and legacy MCP utilities are outside this
formatting gate. The configured strict mypy scope is defined in
`pyproject.toml`.

To verify the local SQLite capabilities directly:

```bash
uv run python -c "import sqlite3; c=sqlite3.connect(':memory:'); c.execute('CREATE VIRTUAL TABLE smoke USING fts5(content)'); c.execute(\"SELECT value FROM json_each('[1]')\")"
```

## Adding a new Knowledge Source

Use this workflow for both human contributors and LLM agents.

### 1. Choose a stable source path

Add one English `.md` file under the appropriate source-type root:

- `Knowledge_base/Articles/...`
- `Knowledge_base/Episodes/...`
- `Knowledge_base/Books/...`

Follow the naming and folder conventions of neighboring sources. The path
relative to `Knowledge_base/` is the permanent source identity. The same path
without `.md` is its case-sensitive `source_slug`.

Do not place a curated source in a hidden directory, `raw_transcripts/`, or
`_summary/`. Files named `INDEX.md` and `TAXONOMY.md` are administrative and are
not indexed as Knowledge Sources.

### 2. Add reviewed frontmatter

Read [`Knowledge_base/TAXONOMY.md`](Knowledge_base/TAXONOMY.md), then add
frontmatter manually:

```yaml
---
title: "Exact source title"
language: en
category: metrics
topics:
  - FTP
source: "Original URL, podcast, or book title"
author: "Author or speaker"
date: "YYYY-MM-DD"
summary: "One or two faithful English sentences."
key_takeaways:
  - "A takeaway directly supported by the source"
---
```

Rules:

- `title`, `category`, `topics`, and `summary` are required by validation.
- The complete source must be English. `language: en` documents that contract;
  ingestion rejects an explicitly non-English value but does not detect the
  language of unlabelled prose.
- Use one canonical category: `metrics`, `hiit`, `zone2`, `strength`,
  `nutrition`, `physiology`, `periodization`, or `book`.
- Copy topic spelling and case from `TAXONOMY.md`. Do not invent a near-synonym
  or change the taxonomy merely to accommodate one ad-hoc tag.
- Use `category: book` for books.
- Do not add `source_type`, chunk IDs, passage boundaries, or citation line
  numbers. Ingestion derives them.
- Include `source`, `author`, `date`, and `key_takeaways` only when known and
  supported. Omit an optional value instead of fabricating it.

### 3. Preserve attributable source content

Use standard Markdown headings to expose the document structure. Preserve
quotes, tables, code fences, and meaningful source wording. Keep relative links
valid. Do not silently translate, synthesize, or rewrite evidence while merely
ingesting a source.

### 4. Synchronize and verify

```bash
# Fix all reported errors. Before synchronization, a sitemap warning for the
# new file is expected.
uv run endurance-kb validate

# Rebuild the passage database and generated master sitemap.
uv run endurance-kb build-index
uv run endurance-kb status
uv run endurance-kb validate

# Use the exact relative path without .md and a phrase unique to the new source.
uv run endurance-kb search "distinct English phrase" \
  --source Articles/example/threshold-testing --format json

PYTHONDONTWRITEBYTECODE=1 uv run python -m unittest discover -s tests -v
git diff --check
git status --short
```

Before committing:

- confirm `status` is fresh and the source-filtered search returns the expected
  Evidence Passage;
- review every validation warning related to the new source;
- include the new source and regenerated `Knowledge_base/INDEX.md`;
- never hand-edit or commit `main/.kb_index.sqlite`;
- update `Books/_summary/INDEX.md` only when the task explicitly includes a
  hand-curated book summary.

The same rebuild is required after editing, renaming, or deleting an existing
source. Renames change source identity and should be deliberate.

## Rules for LLM agents

Before changing the repository:

1. Read [`AGENTS.md`](AGENTS.md), [`CONTEXT.md`](CONTEXT.md), the relevant ADR or
   specification, and `Knowledge_base/TAXONOMY.md`.
2. Claim tracked work through the GitHub issue workflow described in
   [`docs/agents/issue-tracker.md`](docs/agents/issue-tracker.md). If GitHub is
   unavailable or read-only, report that constraint explicitly.
3. Keep source edits scoped. Do not rewrite unrelated evidence, casually rename
   sources, or run corpus-wide standardization.
4. Never edit the generated root `Knowledge_base/INDEX.md` or the local SQLite
   index by hand.
5. Run the add-source verification sequence and report the source path,
   `source_slug`, index status, validation errors, and test result.

## Troubleshooting

| Result | What it means | Action |
| --- | --- | --- |
| `missing_index` | No local Derived Index exists. | Run `uv run endurance-kb build-index`. |
| `stale_index` | A source path/content or taxonomy changed. | Rebuild before searching. |
| `invalid_index` | The database is corrupt or has an old schema. | Run `build-index`; transactional sync replaces it. |
| `unsupported_language` | A source explicitly declares a non-English language. | Remove it from the curated corpus or provide a separately reviewed English source. |
| `corpus_changed_during_sync` | Files changed while synchronization was running. | Stop concurrent edits and rerun `build-index`. |
| `invalid_search` | The query is empty/non-searchable or `--top` is outside 1–20. | Correct the query or limit. |

`status` returns JSON and may exit successfully even when the state is not
fresh. Automation should inspect `state` or `is_fresh`, not only the process
exit code.

## Legacy MCP adapter

The repository still contains `main/mcp_server.py` for local stdio clients. It
delegates to the same explicit English FTS5 index, but it is not the final
hardened MCP contract. Test its current tool calls with:

```bash
uv run python -m main.mcp_server --test
```

For a client configuration, use the repository's absolute `.venv/bin/python`,
arguments `-m main.mcp_server`, and the repository root as `cwd`. See the
[`clone-to-first-query onboarding specification`](docs/prototypes/009-clone-to-first-query-onboarding.md)
for an example.

## Further reading

- [`CONTEXT.md`](CONTEXT.md) — canonical domain vocabulary.
- [`English Evidence Passage Synchronization`](docs/specs/010-english-evidence-passage-sync.md)
  — implemented retrieval contract.
- [`Local retrieval and MCP ADR`](docs/adr/0001-local-hybrid-retrieval-and-mcp-contract.md)
  — architecture and deferred work.
- [`English retrieval foundation`](docs/research/006-english-retrieval-foundation.md)
  — benchmark and model-selection boundaries.
