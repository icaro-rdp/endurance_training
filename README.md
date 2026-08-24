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

> [!TIP]
> Looking for a complete step-by-step guide to configure the MCP server in **Claude Desktop**, **Cursor**, **Claude Code**, or **Codex**? See the [Quickstart Guide](QUICKSTART.md).

Prerequisites:

- macOS, Linux, or Windows 11 through WSL2; native Windows is not supported by
  the current onboarding flow;
- a POSIX-compatible shell for the commands below;
- Git 2.30 or newer;
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

The supported default workflow is a repository clone: the corpus is not bundled
inside the Python wheel. An installed CLI can operate on an external clone by
putting the global path options before the command:

```bash
endurance-kb --kb-dir /absolute/path/to/Knowledge_base \
  --db-path /absolute/path/to/.kb_index.sqlite status
```

`ENDURANCE_KB_DIR` can supply the corpus path instead. An explicit `--kb-dir`
always wins, followed by the environment variable and then
`./Knowledge_base`.

## Repository map

- [`QUICKSTART.md`](QUICKSTART.md) — step-by-step onboarding guide and MCP client configuration.
- [`Knowledge_base/`](Knowledge_base/) — curated Markdown Knowledge Sources.
  - [`Articles/`](Knowledge_base/Articles/) — articles and research notes.
  - [`Episodes/`](Knowledge_base/Episodes/) — curated podcast notes.
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
uv run endurance-kb validate --source Articles/example/source.md
```

Validation errors are blocking. Warnings are advisory and can be numerous for
converted books with unresolved original links. The CLI prints every error but
only the first 15 warnings, so a zero exit code does not mean there were no
warnings. The add-source workflow below includes a targeted command that prints
all warnings for the new file.

### Standardize frontmatter

`standardize` writes files; it is not a preview command. It adds frontmatter
only to documents that have none and never replaces existing metadata. Prefer
writing and reviewing frontmatter manually for a new source. The command fails
instead of inventing a category, topic, source, author, or date when those
values cannot be inferred safely.

```bash
uv run endurance-kb standardize
```

Review every resulting source edit before synchronization.

## Testing changes

Install the locked development environment with `uv sync --locked`, then run:

```bash
PYTHONDONTWRITEBYTECODE=1 uv run python -m unittest discover -s tests -v
uv run ruff check .
uv run ruff format --check .
uv run mypy
git diff --check
```

The configured strict mypy scope is defined in `pyproject.toml`.

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

Follow the naming and folder conventions of neighboring sources. The path
relative to `Knowledge_base/` is the permanent source identity. The same path
without `.md` is its case-sensitive `source_slug`.

Do not place a curated source in a hidden directory, `raw_transcripts/`, or
`_summary/`. Files named `INDEX.md` and `TAXONOMY.md` are administrative and are
not indexed as Knowledge Sources.

### 2. Add reviewed frontmatter

Read the canonical frontmatter contract in
[`Knowledge_base/TAXONOMY.md`](Knowledge_base/TAXONOMY.md), then add frontmatter
manually:

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
---
```

When directly supported takeaways have been deliberately reviewed, add the
optional field:

```yaml
key_takeaways:
  - "A takeaway directly supported by the source"
```

Rules:

- Every field in the main template is required by the canonical new-source
  contract. Automated validation requires `title`, `category`, `topics`, and
  `summary`, rejects malformed YAML and explicit non-English language metadata,
  and reports noncanonical categories or topics as warnings. That narrower
  automated check does not make the other main fields optional.
- The complete source must be English. `language: en` documents that contract;
  ingestion rejects an explicitly non-English value but does not detect the
  language of unlabelled prose. Reviewed legacy sources without `language` are
  interpreted as English, but new sources may not rely on that compatibility
  rule.
- Use one canonical category: `metrics`, `hiit`, `zone2`, `strength`,
  `nutrition`, `physiology`, or `periodization`.
- Copy topic spelling and case from `TAXONOMY.md`. Do not invent a near-synonym
  or change the taxonomy merely to accommodate one ad-hoc tag.
- Do not add `source_type`, chunk IDs, passage boundaries, or citation line
  numbers. Ingestion derives them.
- Record the real source, author, and publication date. Use `author: "Unknown"`
  only when the original identifies no author. A new source still needs a real
  `YYYY-MM-DD` publication date; research or escalate a missing date rather than
  inventing one or changing the schema. Do not ingest evidence whose provenance
  cannot be established.
- `key_takeaways` is optional. Include only directly supported takeaways that
  have been deliberately curated; otherwise omit the field.

### 3. Preserve attributable source content

Use standard Markdown headings to expose the document structure. Preserve
quotes, tables, code fences, and meaningful source wording. Keep relative links
valid. Do not silently translate, synthesize, or rewrite evidence while merely
ingesting a source.

### 4. Synchronize and verify

```bash
# Targeted validation prints every warning for the new source. Fix all errors;
# before synchronization, its sitemap warning is expected.
uv run endurance-kb validate \
  --source Articles/example/threshold-testing.md

# Global validation reports corpus health but displays only its first 15
# warnings.
uv run endurance-kb validate

# Rebuild the passage database and generated master sitemap.
uv run endurance-kb build-index
uv run endurance-kb status
uv run endurance-kb validate

# Global validation shows only the first 15 warnings. Targeted validation shows
# every warning for one exact path relative to Knowledge_base.
uv run endurance-kb validate \
  --source Articles/example/threshold-testing.md

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
- review every warning printed by the targeted new-source command;
  `Warnings Found: 0` means it found none for that path;
- include the new source and regenerated `Knowledge_base/INDEX.md`;
- never hand-edit or commit `main/.kb_index.sqlite`.

The same rebuild is required after editing, renaming, or deleting an existing
source. Renames change source identity and should be deliberate.

## Rules for LLM agents

Before changing the repository:

1. Read [`AGENTS.md`](AGENTS.md), [`CONTEXT.md`](CONTEXT.md), the relevant ADR or
   specification, and `Knowledge_base/TAXONOMY.md`.
2. Claim tracked work through the GitHub issue workflow described in
   [`docs/agents/issue-tracker.md`](docs/agents/issue-tracker.md). If GitHub is
   unavailable or read-only, report the constraint and stop. Proceed without an
   assignment only when the user explicitly authorizes that exception, and
   document the authorization.
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
| `invalid_index_path` | The selected output could overwrite source data or is not an index filename. | Choose a nonsymlink `.sqlite`, `.sqlite3`, or `.db` path outside `Knowledge_base`. |
| `knowledge_base_not_found` | The configured corpus directory does not exist. | Run from the repository root, set `ENDURANCE_KB_DIR`, or pass global `--kb-dir`. |
| `invalid_knowledge_base` | The selected directory is not the canonical corpus root. | Select the `Knowledge_base` directory containing `TAXONOMY.md`. |
| `empty_corpus` | The selected directory has no curated sources. | Correct `--kb-dir` or add a valid source before building. |
| `invalid_source` | A source has malformed YAML or violates the ingestion shape. | Fix the named source; the previous database remains intact. |
| `source_not_found` | A targeted validation path is not a curated source. | Use the exact case-sensitive path relative to `Knowledge_base`, including `.md`. |
| `unsupported_language` | A source explicitly declares a non-English language. | Remove it from the curated corpus or provide a separately reviewed English source. |
| `corpus_changed_during_sync` | Files changed while synchronization was running. | Stop concurrent edits and rerun `build-index`. |
| `invalid_search` | The query is empty/non-searchable or `--top` is outside 1–20. | Correct the query or limit. |

`status` returns JSON and may exit successfully even when the state is not
fresh. Automation should inspect `state` or `is_fresh`, not only the process
exit code.

## MCP server for LLMs

The repository includes a Model Context Protocol (MCP) server built with the
official MCP Python SDK (`main/mcp_server.py`), exposing `KBEngine` capabilities
over standard I/O (stdio) to connected LLMs (Claude Desktop, Cursor, Antigravity,
LibreChat, etc.).

### Tools

- `search_passages`: Lexical BM25 retrieval over citation-stable Evidence
  Passages with line-range citations (`#L45-L89`), section breadcrumbs, and
  optional `category`, `topic`, and `source_slug` filters.
- `search_knowledge_base`: Backward-compatible alias for `search_passages`.
- `get_passage`: Fetch complete metadata and content of an Evidence Passage by
  its stable `chunk_id`.
- `get_document`: Retrieve full Markdown text of a curated Knowledge Source
  with strict path containment against directory traversal.
- `get_kb_status`: Check Derived Index freshness (`fresh`, `stale`, `missing`),
  document count, passage count, and content digests.
- `get_taxonomy`: Get canonical categories and allowed topics.
- `get_sitemap`: Get the master document catalog.
- `validate_kb`: Run health and frontmatter validation.

### Resources

- `endurance-kb://sitemap`: Master document sitemap.
- `endurance-kb://taxonomy`: Canonical taxonomy structure.
- `endurance-kb://status`: Current index freshness status.

### Self-test

Verify tool and resource execution locally:

```bash
uv run endurance-kb-mcp --test
```

### LLM client configuration

For comprehensive step-by-step setup guides across **Claude Desktop**, **Cursor IDE**, **Claude Code**, **OpenAI Codex**, and other MCP-compatible clients, see the [Quickstart Guide](QUICKSTART.md#6-connect-to-llm-clients--coding-assistants).

Example configuration for `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "endurance-kb": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/endurance_training",
        "run",
        "endurance-kb-mcp"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

Or using the virtual environment directly:

```json
{
  "mcpServers": {
    "endurance-kb": {
      "command": "/absolute/path/to/endurance_training/.venv/bin/endurance-kb-mcp",
      "cwd": "/absolute/path/to/endurance_training",
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## Further reading

- [`CONTEXT.md`](CONTEXT.md) — canonical domain vocabulary.
- [`English Evidence Passage Synchronization`](docs/specs/010-english-evidence-passage-sync.md)
  — implemented retrieval contract.
- [`Local retrieval and MCP ADR`](docs/adr/0001-local-hybrid-retrieval-and-mcp-contract.md)
  — architecture and deferred work.
- [`English retrieval foundation`](docs/research/006-english-retrieval-foundation.md)
  — benchmark and model-selection boundaries.
