# English Knowledge Corpus Audit

**Snapshot date:** 2026-08-20

**Scope:** Curated Markdown returned by `iter_kb_documents()`

**Status:** Foundation baseline; refresh before any corpus-wide migration

## Purpose

This document records the current shape of the English-only Knowledge Base and the normalization work that remains. It replaces the earlier 60-document audit, which predates the podcast expansion and must not be used for implementation estimates.

The retrieval corpus contains curated Markdown under `Knowledge_base/`. Administrative indexes, `TAXONOMY.md`, hidden directories, and `raw_transcripts/` are not Knowledge Sources.

## Current inventory

| Source type | Documents | Lines | Shell word count |
| --- | ---: | ---: | ---: |
| Articles | 41 | 6,211 | 46,312 |
| Podcast notes | 218 | 32,608 | 326,322 |
| Books | 4 | 18,122 | 382,608 |
| **Total** | **263** | **56,941** | **755,242** |

The repository also contains 201 raw transcript Markdown files and three administrative Markdown files. Those 204 files are excluded by the canonical walker and are not indexed.

These counts describe the working tree on the snapshot date. They are diagnostic evidence, not constants that tests should hard-code.

## English-only invariant

The first implementation supports English Knowledge Sources only.

- Missing language metadata is interpreted as `en`.
- Explicit `language: en`, `language: English`, or equivalent inline English metadata is accepted.
- A source that explicitly declares any other language fails synchronization with `unsupported_language`.
- `source_type` is derived from the first path component: `Articles`, `Episodes`, or `Books`. It does not need to be duplicated in frontmatter.

No current curated source has a frontmatter `language` or `source_type` field. That is valid for this English-only foundation because the implementation supplies both values deterministically.

## Remaining normalization findings

The old defect totals are obsolete. A narrow recount against the current corpus found:

- 59 of 263 sources do not contain `key_takeaways`.
- Four books still declare `category: general`; ingestion normalizes these passages to `category: book`.
- Three books have no Markdown headings. The production chunker recovers English chapter anchors and uppercase bold section titles where present.
- Link-health totals have not been remeasured for the expanded corpus. The former broken-link count must not be quoted as current.

Normalization must preserve substantive source text. Missing takeaways should be curated deliberately rather than synthesized automatically during indexing.

## Canonical ingestion metadata

Each Knowledge Source should provide usable values for:

- `title`
- `author`
- `category`
- `topics`
- `source`
- `date`
- `summary`
- `key_takeaways`, when curated takeaways are available

The passage layer additionally derives `language`, `source_type`, repository-relative path, and source slug. Invalid YAML or an unclosed frontmatter block is an ingestion error; it is not silently ignored.

## Migration order

1. Re-run this inventory from the canonical walker immediately before migration.
2. Normalize the four book categories and curate the 59 missing takeaway lists separately from indexing.
3. Improve headings and remove obsolete conversion links only when the change is mechanically reviewable and preserves source meaning.
4. Run validation, then perform explicit Corpus Synchronization.
5. Record new counts from the synchronized index rather than copying values from this report.

## Implementation references

- `main/utils/kb_engine/walker.py` — canonical source selection
- `main/utils/kb_engine/chunker.py` — English-only metadata and structure handling
- `main/utils/kb_engine/models.py` — Evidence Passage contract
- `main/utils/kb_engine/sync.py` — deterministic corpus manifest
