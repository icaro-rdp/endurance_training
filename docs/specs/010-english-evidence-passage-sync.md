# English Evidence Passage Synchronization

**Status:** Implemented
**Parent:** [Build a private evidence-grounded endurance knowledge system](https://github.com/icaro-rdp/endurance_training/issues/1)
**Scope:** First production increment

## Decision

The Knowledge Base accepts English sources and English queries only. This
explicitly supersedes the multiple-language requirements in the parent issue
and earlier research notes. The non-English book source is removed from the
curated corpus rather than translated or indexed.

English is the only supported and benchmarked query language. Query-language
identification is a caller-side precondition; this increment deliberately does
not add a language detector or claim behavior for unsupported query languages.

**Tracker exception:** the available GitHub integration was read-only, so a
scoped task ticket could not be created, assigned, or linked before work. The
user directly authorized this implementation against the parent issue.

This increment establishes the retrieval foundation before model-dependent
semantic search or MCP expansion:

1. Parse each curated Markdown Knowledge Source into immutable Evidence
   Passages that retain source metadata, section hierarchy, and exact 1-based
   source line locators.
2. Use canonical paths relative to `Knowledge_base/` as source identity.
3. Derive passage IDs from source identity, hierarchy, and passage content, not
   mutable line positions.
4. Bound normal passages with an explicit word policy. Preserve indivisible
   Markdown blocks and label any oversized atomic block instead of truncating it.
5. Build one local SQLite FTS5 Derived Index only through an explicit,
   transactional synchronization command.
6. Hash curated source paths and contents plus `TAXONOMY.md` to detect stale
   indexes. Generated `INDEX.md` catalogues do not affect freshness.
7. Refuse search when the Derived Index is missing, stale, or invalid; search
   never rebuilds it implicitly.

## Acceptance criteria

- Every current English source chunks without a network call or model download.
- Chunking and the corpus digest are deterministic.
- Passage IDs are unique across the corpus and stable when only preceding line
  positions change.
- Each passage records `author`, `language=en`, `source_type`, `category`,
  `topics`, its canonical relative source path, hierarchy, and citation lines.
- Declared non-English sources fail synchronization with a clear error.
- Explicit synchronization atomically replaces the previous database only
  after a successful full build.
- Add, edit, delete, rename, and taxonomy changes mark the index stale.
- Category, topic, and source filters match canonical values exactly.
- Unit, integration, full-corpus smoke, formatting, and static type checks pass.

## Deferred

- Dense embeddings, score fusion, reranking, diversification, and abstention.
- Model selection until the English-only benchmark has executable relevance
  judgments against produced Evidence Passage IDs.
- A hardened FastMCP server and corpus-wide frontmatter migration.
