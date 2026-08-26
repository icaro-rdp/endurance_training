# PostgreSQL/Supabase Knowledge Source Persistence

**Snapshot date:** 2026-08-26  
**Status:** Decision research; no production implementation  
**Question:** Should PostgreSQL/Supabase become the authoritative store for Knowledge Sources instead of Markdown files in Git?

## Recommendation

Yes. Make PostgreSQL the authoritative store for Knowledge Source content,
metadata, lifecycle, and revision history. Use Supabase as the hosted PostgreSQL
provider, and use a PostgreSQL + pgvector container for the local Docker
application. Keep Git authoritative for database migrations, taxonomy seed data,
code, and deterministic export tooling—not for live Knowledge Source records.

This is a better fit for browser create/edit/archive because a publication can be
one validated transaction with concurrency control, immutable revisions, and a
stable published pointer. PostgreSQL provides constraints, foreign keys,
transactions, row locks, and MVCC for safe concurrent access
([PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html),
[PostgreSQL MVCC](https://www.postgresql.org/docs/current/mvcc-intro.html)). MVCC
is not, by itself, permanent editorial history; the durable revision log must be
an explicit application schema. PostgreSQL triggers could capture row changes,
but an explicit append-only revision model makes publishing and restoration part
of the domain rather than an incidental audit side effect
([PostgreSQL `CREATE TRIGGER`](https://www.postgresql.org/docs/current/sql-createtrigger.html)).

Do not make both Git and PostgreSQL writable authorities. A dual-authority model
must resolve conflicting edits, ordering, deletion, and failure halfway through a
two-system write. It adds the most failure modes while leaving the user unsure
which copy is true.

## Current corpus facts

The canonical walker in `main/utils/kb_engine/walker.py` currently selects:

| Fact | Current value |
| --- | ---: |
| Knowledge Sources | 259 |
| Articles | 41 |
| Podcast notes | 218 |
| Source bytes | 2,956,837 |
| Source lines | 39,041 |
| Whitespace-delimited words | 374,146 |
| Categories in use | 7 |
| Distinct topics in use | 37 |
| Source-topic assignments | 926 |
| Indexed Evidence Passages | 1,957 |
| Indexed passage characters | 2,429,374 |

The current validator reports zero errors and zero warnings across all 259
sources. All 259 omit an explicit `language` field and rely on the reviewed
legacy `en` default. Migration must materialize that default deliberately; it
must not mistake omission for unknown language. These live counts supersede the
older 263-source corpus audit and should be refreshed at migration time.

At roughly 3 MB of source Markdown and 1,957 passages, storage scale is not a
reason to retain filesystem authority. It is also too early to assume an
approximate vector index is necessary: pgvector supports exact nearest-neighbor
queries as well as HNSW and IVFFlat, and its own documentation recommends
monitoring approximate recall against exact search
([pgvector](https://github.com/pgvector/pgvector)). Preserve the existing
benchmark gate when choosing the production vector index.

## Proposed authority and data model

The schema should distinguish stable source identity, immutable editorial
revisions, and rebuildable retrieval data.

### Authoritative tables

- `knowledge_sources`: stable UUID, unique slug, source type, lifecycle
  (`draft`, `published`, `archived`), `published_revision_id`, audit timestamps,
  and archive metadata. Slugs are locators, not primary identity.
- `knowledge_source_revisions`: append-only UUID, source UUID, monotonically
  increasing revision number, parent revision, Markdown body, title, summary,
  language, category, author, source/provenance URI or name, publication date,
  content SHA-256, editor identity, and creation time.
- `categories` and `topics`: controlled taxonomy rows. Category membership and
  the revision-to-topic join are revisioned metadata, because changing them
  changes the published representation. Use foreign keys and uniqueness for
  identity; reserve JSONB for genuinely unstructured optional metadata rather
  than placing the full frontmatter contract in one opaque column. PostgreSQL's
  primary-key, unique, check, and foreign-key constraints can enforce the
  structural invariants at write time
  ([PostgreSQL `CREATE TABLE`](https://www.postgresql.org/docs/current/sql-createtable.html)).
- Optional curated `key_takeaways` should either be ordered child rows or a
  narrowly validated array. It remains absent unless a human curated it.

Store Markdown as `text`; do not store executable MDX. YAML frontmatter becomes
an import/export representation of the structured revision fields, not a second
canonical schema. Python remains responsible for the richer domain rules that
SQL cannot faithfully express, including the complete Markdown and provenance
contract. Database constraints provide a second, narrower integrity boundary
such as `language = 'en'`, valid foreign keys, nonempty required text, unique
slugs, and unique revision numbers.

### Derived retrieval tables

- `evidence_passages`: source revision UUID, stable chunk ID, ordinal, section
  hierarchy, Markdown line range or character offsets, passage text, size status,
  chunker version, and content hash.
- A stored/generated English `tsvector` plus GIN index for lexical retrieval.
  PostgreSQL documents GIN as the preferred full-text index type, and recommends
  naming the text-search configuration explicitly so index contents remain
  reproducible
  ([PostgreSQL text-search indexes](https://www.postgresql.org/docs/current/textsearch-indexes.html),
  [tables and indexes](https://www.postgresql.org/docs/current/textsearch-tables.html)).
- A `vector(384)` column for the current BGE-small embeddings, plus embedding
  model/version metadata. Supabase exposes pgvector-backed vector columns and
  requires their dimension to match the embedding model
  ([Supabase vector columns](https://supabase.com/docs/guides/ai/vector-columns)).

Supabase documents the same intended hybrid shape—`tsvector`, pgvector, GIN,
vector indexing, and reciprocal-rank fusion—so the selected hosted platform can
support the existing retrieval architecture
([Supabase hybrid search](https://supabase.com/docs/guides/ai/hybrid-search)).
That confirms feasibility, not retrieval parity: PostgreSQL full-text ranking is
not SQLite FTS5 BM25, so the current labelled benchmark must compare the port
before the old index is retired.

Only passages belonging to each non-archived source's published revision should
participate in Direct Search. Passage generation and embeddings remain
rebuildable processing outputs; revisions remain the recoverable source of
truth.

## Safe browser editorial workflow

All browser writes should be `Next.js -> FastAPI -> PostgreSQL`. Do not place a
Supabase service-role key or a direct privileged table client in the browser.
Supabase supports trusted servers using direct database connections and allows
the Data API to be disabled when an application accesses data only through a
server layer
([Supabase secure data](https://supabase.com/docs/guides/database/secure-data)).

Recommended write contract:

1. The editor sends Markdown, structured metadata, and the revision ID on which
   the edit was based.
2. FastAPI authenticates and authorizes the administrator, parses Markdown,
   validates taxonomy/provenance, sanitizes the reader rendering contract, and
   computes a content hash.
3. The service locks the stable source row and rejects a stale base revision
   instead of overwriting a concurrent edit.
4. It inserts a new immutable draft revision. Chunking and embedding can run in
   a staging state; an incomplete build is never searchable.
5. Publication transactionally marks the revision ready and updates the
   source's `published_revision_id`. Readers therefore observe either the old
   complete revision or the new complete revision, never half of each.
6. “Delete” in v1 archives the stable source and excludes it from normal library
   and search results. It does not erase revisions or break citations. Permanent
   purge should be a separate, explicitly destructive future operation.
7. Restore creates a new revision copied from an older one; history remains
   monotonic and inspectable.

If any tables are exposed through Supabase's Data API, enable RLS, revoke default
client privileges, grant back only the intended operations, and test every
policy. Supabase warns that exposed tables without RLS can be reachable by roles
with grants and that the service role bypasses RLS and must stay server-side
([Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security)).
For the proposed FastAPI-only boundary, prefer an unexposed application schema
and a least-privileged backend database role; RLS can remain defense in depth.

## Citation and provenance contract

File URIs and mutable line links cannot be the hosted canonical citation. Use a
versioned product locator such as:

```text
/sources/{source_id}/revisions/{revision_id}#passage={chunk_id}
```

Every search/MCP result should carry source UUID and slug, revision UUID,
passage ID, title, author, provenance, section hierarchy, and line range within
the immutable revision Markdown. The normal reader may show the current
revision, but the canonical citation resolves the exact historical revision.
Archived sources remain retrievable by an exact authorized citation even though
they are absent from discovery.

This preserves the current “inspect the exact evidence” property while removing
its dependency on a local checkout. Retaining the exact imported Markdown and
its SHA-256 also allows a migration or export to prove byte-level provenance.

## Local Docker and hosted Supabase

Use one portable SQL migration history for both environments.

- **Local product:** Docker Compose runs Next.js, FastAPI, and a pinned
  `pgvector/pgvector` PostgreSQL image with a named data volume. The official
  pgvector project publishes images based on the standard PostgreSQL image
  ([pgvector Docker installation](https://github.com/pgvector/pgvector#docker)).
  This is the smallest offline-capable runtime for the chosen Auth.js + FastAPI
  boundary.
- **Hosted product:** apply the same migrations to Supabase PostgreSQL and enable
  the `vector` extension, which Supabase officially supports
  ([Supabase pgvector extension](https://supabase.com/docs/guides/database/extensions/pgvector)).
- **Development option:** the Supabase CLI can recreate its complete local stack
  in Docker from committed config, migrations, and seed data. Supabase explicitly
  says this local stack is for development only and must not be exposed as a
  production service
  ([Supabase local workflow](https://supabase.com/docs/guides/local-development/cli-workflows)).

The full local Supabase stack is unnecessary in v1 unless the application adopts
Supabase Auth, Storage, Realtime, or direct browser Data API access. Avoid using
Supabase-only database features in the core schema until a concrete requirement
earns that coupling. Pin and verify the PostgreSQL and pgvector versions in both
environments.

## MCP and CLI boundary

FastAPI, MCP, and CLI should remain adapters over the same Python application
services and repository interfaces:

```text
Next.js -> FastAPI ---+
External LLM -> MCP --+-> Python application services -> PostgreSQL
Operator -> CLI ------+
```

MCP does not require OpenRouter. An external LLM can call the same retrieval and
document-reading services through MCP when application-owned AI Search is
unconfigured. The CLI should provide migration/import/export, validation,
reindexing, status, and retrieval operations through the same service boundary;
it should not grow a separate SQL interpretation of the domain.

## Backup, export, and recovery

Database authority is safe only with an explicit recovery policy:

- Supabase currently provides automatic daily backups for Pro, Team, and
  Enterprise projects; it recommends regular CLI dumps and off-site backups for
  free-tier projects. Point-in-Time Recovery is a paid add-on
  ([Supabase database backups](https://supabase.com/docs/guides/platform/backups)).
- Independently schedule encrypted logical dumps outside the database host and
  test restoration. PostgreSQL `pg_dump` creates consistent exports while the
  database is in use, but its documentation says it is generally not the sole
  mechanism for regular production backup
  ([PostgreSQL `pg_dump`](https://www.postgresql.org/docs/current/app-pgdump.html)).
- A Docker named volume is persistence, not backup. Local operation needs an
  explicit `backup`/`restore` command writing outside that volume.
- Provide a deterministic portable export: one Markdown file per published or
  archived revision (as selected), validated YAML frontmatter, and a manifest of
  stable IDs, revision numbers, hashes, and taxonomy version. The export is an
  escape hatch and review artifact, not a writable peer authority.
- Define and test both disaster restore and single-source editorial rollback.
  Backups solve database loss; immutable revisions solve ordinary bad edits.

RPO, RTO, retention length, encryption destination, and hosted plan remain
deployment decisions, but they must be explicit before production data is made
database-only.

## Trade-off summary

| Option | Strengths | Costs / risks | Decision |
| --- | --- | --- | --- |
| Git/Markdown authoritative, DB projection | Excellent diffs, offline files, established corpus | Browser writes require a Git credential/worktree/commit/publish pipeline; hosted filesystem is not authority; publication and search synchronization are two systems | Reject for the product authority |
| PostgreSQL authoritative, Git for migrations and exports | Natural browser CRUD, transactions, immutable revisions, one local/hosted retrieval store, stable product citations | Must build revision workflow, backup/export/restore, and migration tooling; SQL FTS parity must be measured | **Adopt** |
| Writable Git and DB | Both editing styles appear available | Conflict resolution, dual-write failure, unclear deletion and authority | Reject |

## Migration gates

1. Commit a final pre-migration corpus snapshot/tag and record every selected
   relative path and SHA-256.
2. Create schema migrations, local pgvector Docker service, and append-only
   editorial workflow before changing authority.
3. Import all sources into staging, materializing reviewed defaults such as
   `language = 'en'`; validate counts, hashes, taxonomy links, and provenance.
4. Generate passages with an explicit chunker version and embeddings with an
   explicit model version. Verify all current sources and passages are
   attributable to one revision.
5. Run the lexical/hybrid benchmark and compare citation integrity and latency
   with the current SQLite path. Do not claim parity from schema similarity.
6. Prove create, concurrent-edit rejection, publish, archive, restore, full
   export, logical dump, and clean restore locally.
7. Run the same migrations and checks on a Supabase staging project.
8. Switch FastAPI, MCP, and CLI together to the shared PostgreSQL repository.
   Keep the old Markdown snapshot read-only for a defined rollback window, then
   remove the dual read path.

## Decision still needed before implementation

The persistence direction is clear, but a design ticket should fix the exact
publication state machine, revision-retention policy, stable citation URL, and
backup RPO/RTO. The “tagging system” also needs one vocabulary decision: whether
it means controlled taxonomy topics, free-form reader tags, Git release tags for
migrations, or more than one of these. These concepts should not share one
ambiguous `tags` field.
