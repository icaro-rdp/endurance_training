# Superseded MCP Conformance Research

**Document ID:** `docs/research/004-mcp-conformance.md`

**Status:** Superseded

**Original date:** 2026-08-10

## Notice

This report previously proposed an MCP architecture before the English passage
retrieval foundation was implemented. Its protocol examples, client commands,
index-freshness rules, and tool recommendations are no longer implementation or
onboarding guidance.

In particular, do not rely on the former assumptions about hybrid retrieval,
modification-time freshness, implicit index rebuilding, machine-specific paths,
or an already-hardened MCP contract. The active baseline is English lexical
passage retrieval over an explicitly synchronized, content-fingerprinted SQLite
index. The existing MCP adapter remains legacy and its final evidence-oriented
contract is deferred.

## Active references

- [`Local English Passage Retrieval Foundation & MCP Direction`](../adr/0001-local-hybrid-retrieval-and-mcp-contract.md)
  is the accepted architecture decision.
- [`Clone to First Query`](../prototypes/009-clone-to-first-query-onboarding.md)
  contains the current portable onboarding and optional legacy-adapter example.
- [`README.md`](../../README.md) contains current commands, test instructions,
  and operational warnings.
- [`CONTEXT.md`](../../CONTEXT.md) defines the active domain and architecture
  vocabulary.

This file remains only as a pointer for historical issue references. New MCP
research must begin from the active ADR and must not revive superseded behavior
without a new decision and executable evidence.
