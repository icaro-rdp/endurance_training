# Production Evidence Passage Chunking Contract

**Date:** 2026-08-20

**Status:** Implemented

**Implementation:** `main/utils/kb_engine/chunker.py`

## Purpose

The production chunker turns one curated English Markdown Knowledge Source into bounded, attributable Evidence Passages. It preserves source identity, section context, and physical line locations without changing the source files.

The former standalone prototype has been removed. This document describes the production implementation and its tested exceptions.

## Evidence Passage schema

Each immutable `EvidencePassage` contains:

| Field | Meaning |
| --- | --- |
| `chunk_id` | Stable source-and-content identifier |
| `source_slug` | Repository-relative source path without `.md` |
| `rel_path` | Repository-relative Markdown path |
| `title`, `author`, `source` | Source provenance |
| `language` | Always `en` in the first implementation |
| `source_type` | `article`, `podcast`, or `book`, derived from the path |
| `category`, `topics` | Taxonomy metadata |
| `section_hierarchy` | Document title plus active heading breadcrumbs |
| `start_line`, `end_line` | One-based physical source-line span |
| `content` | Passage text drawn from the cited span |
| `word_count`, `char_count` | Passage size diagnostics |
| `citation` | Absolute file URI with a line fragment |
| `size_status` | `within_policy`, `undersized_section`, or `oversized_atomic_block` |

The schema is defined in `main/utils/kb_engine/models.py`.

## Identifier stability

The base identifier hashes:

1. the repository-relative source slug;
2. the section hierarchy;
3. the normalized passage content.

Line numbers are deliberately excluded. Inserting blank lines before unchanged evidence updates its citation but not its identifier. Repeated identical passages receive a deterministic occurrence suffix so identifiers remain unique within a document.

Changing the source path, section identity, or evidence text intentionally changes the identifier.

## Metadata and language rules

Metadata is read from YAML frontmatter, then from supported inline fields, then from deterministic path or filename fallbacks.

- Missing language metadata defaults to English.
- Explicit English metadata is accepted.
- An explicitly non-English source raises `unsupported_language`.
- Book passages whose source metadata uses `general`, `book`, or `books` are normalized to category `book`.
- Invalid YAML mappings and unclosed frontmatter fail clearly.

## Structure recovery

The chunker recognizes:

- Markdown headings from H1 through H6;
- English EPUB chapter links;
- English EPUB part links;
- short uppercase bold section headings.

Heading-like text inside fenced code is ignored. A repeated H1 matching the document title is removed from the breadcrumb to avoid duplicate hierarchy entries.

## Passage sizing

The default word-count policy is:

- target: 350 words;
- minimum: 80 words;
- maximum: 600 words.

Paragraph-like blocks are accumulated toward the target. A passage is flushed before exceeding the maximum, or after exceeding the target when it already meets the minimum. Small neighboring drafts are coalesced when the merged passage remains within the maximum.

There is no sliding overlap. Every repeated word must come from the source rather than from synthetic overlap.

### Explicit exceptions

- Fenced code, Markdown tables, and blockquotes are atomic blocks.
- An atomic block larger than the maximum is preserved intact and marked `oversized_atomic_block`.
- A section that cannot be safely merged to the minimum is retained and marked `undersized_section`.
- Oversized non-atomic prose is split by physical line and, when necessary, by word windows within one line. Multiple passages may therefore share the same single-line locator.

These statuses make exceptions inspectable; the implementation never silently truncates evidence.

## Citation behavior

Line ranges refer to the original Markdown file after frontmatter. The citation URI is rendered from the current absolute path at chunking time. Stored identity remains repository-relative, so a clone in another directory produces the same passage identifiers and different local citation URIs.

## Verification

`tests/test_chunker.py` covers:

- frontmatter line offsets and metadata propagation;
- standard and recovered headings;
- identifier stability after preceding blank-line insertion;
- source-path collision resistance;
- English-only enforcement;
- book-category normalization;
- long prose splitting without word loss;
- oversized atomic-block diagnostics;
- deterministic output across instances.

Passage persistence, synchronization, lookup, filtering, and stale-index behavior are covered separately in `tests/test_passage_index.py`.
