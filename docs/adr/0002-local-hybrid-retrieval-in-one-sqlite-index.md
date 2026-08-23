# 2. Local Hybrid Retrieval in One SQLite Derived Index

The Knowledge Base will retain FTS5 lexical search and add local embedding-based vector search through `sqlite-vec` in the same reproducible Derived Index. A connected hosted LLM may call the MCP server for Grounded Synthesis, but the corpus, Athlete Query, and embeddings remain local; hybrid retrieval must demonstrate improvement against the lexical benchmark before becoming the default ranking path. Retrieval evaluation ranks ten candidates and MCP returns up to ten Evidence Passages, stopping at a benchmark-calibrated relevance threshold rather than filling a fixed quota. MCP exposes only retained relevant evidence or an `insufficient_evidence` result; ranking scores and cutoff mechanics remain internal. A low-scoring partial match is insufficient evidence and triggers hosted-LLM external-source search rather than a weak KB-grounded answer. External sources are cited only in the resulting answer and are never added automatically to the curated Knowledge Base. Model selection requires an in-repository benchmark of at least 30 passage-labelled Athlete Queries; MTEB/BEIR retrieval results may shortlist candidates but cannot substitute for corpus-specific measurement.

## MCP Client Retrieval Protocol

The hosted LLM checks index freshness before substantive retrieval. It uses `search_passages` for one focused evidence intent, or decomposes a compound or comparative Athlete Query into two to four independent evidence-seeking sub-queries and uses `search_multi_passages`. Grounded Synthesis uses only returned Evidence Passages, cites them, and labels uncertainty rather than treating absence of a result as evidence.

## Considered Options

- **Separate Chroma or LanceDB store**: rejected for now because a personal, local Knowledge Base does not justify a second persistence and synchronization system.
- **Hosted embedding API**: rejected because it would disclose Knowledge Source text and Athlete Queries to the provider.
