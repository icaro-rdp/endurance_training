# Hybrid Passage Retrieval & Query Intelligence Architecture

**Document:** `docs/specs/011-hybrid-retrieval-architecture.md`  
**Status:** Superseded design draft; not implemented<br>
**Context:** [Local Hybrid Retrieval in One SQLite Derived Index](../adr/0002-local-hybrid-retrieval-in-one-sqlite-index.md)<br>
**Parent Issue:** [Build a private evidence-grounded endurance knowledge system](https://github.com/icaro-rdp/endurance_training/issues/1)

---

> **Status note (2026-08-23):** This document describes an earlier aspirational
> hybrid design. The current implementation remains lexical FTS5, and the
> approved replacement direction is defined by ADR 0002. Do not treat the
> implementation claims below as current behavior.

## 1. Architecture Overview & Mental Model

The goal of this architecture is to provide an evidence-grounded, private, offline-capable search pipeline for endurance training knowledge.

The system is structured as a **cohesive retrieval pipeline**:

```
                       ┌───────────────────────────────┐
                       │   Agent & Query Intelligence  │
                       │ • Sub-query decomposition     │
                       │ • Taxonomy category routing   │
                       │ • Context formatting for LLMs │
                       └───────────────┬───────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
     ┌─────────────────────────────┐       ┌─────────────────────────────┐
     │   FTS5 Lexical Foundation   │       │    Dense Vector Layer       │
     │ • Column-weighted BM25      │       │ • Semantic text embeddings  │
     │ • Stopword filtering        │       │ • Cosine similarity scoring │
     │ • Domain synonym expansion  │       │ • Offline CPU model/matrix  │
     └──────────────┬──────────────┘       └──────────────┬──────────────┘
                    │                                     │
                    └──────────────────┬──────────────────┘
                                       ▼
                       ┌───────────────────────────────┐
                       │ Reciprocal Rank Fusion (RRF)  │
                       │  Merges sparse + dense ranks  │
                       └───────────────┬───────────────┘
                                       ▼
                         Citation-Stable Passages
```

---

## 2. FTS5 Lexical Foundation

### Problem Statement
Standard full-text search tokenizes queries naively and treats all document fields equally. A query like *"How to increase my FTP over a 12-week block?"* suffers from:
1. **Filler word noise**: Words like `how`, `to`, `over`, `a` dilute the search.
2. **Field unbalance**: A passage mentioning `"FTP"` once in the body scores similarly to a passage with `"FTP"` in its title and primary topic.
3. **Acronym blindness**: Searching for `"MLSS"` misses passages that only use `"Maximal Lactate Steady State"`.

### Design & Solution

#### A. Domain-Aware Query Tokenizer & Stopword Filter
Before passing tokens to SQLite FTS5, queries undergo normalization:
1. Case normalization and punctuation cleanup.
2. Removal of common English conversational stop words (`how`, `what`, `is`, `are`, `can`, `do`, `does`, `the`, `a`, `an`, `of`, `for`, `in`, `on`, `with`, `and`, `to`, `over`, `my`, `your`, etc.).
3. **Preservation of endurance domain tokens**: Critical keywords (`vo2`, `vo2max`, `ftp`, `tte`, `lt1`, `lt2`, `vt1`, `vt2`, `w'`, `30/15`, `4x8`, `4x4`, `4x16`, `zone2`, `fatmax`) are protected from accidental stripping.

#### B. Dedicated Domain Synonyms Module (`main/utils/kb_engine/synonyms.py`)
An isolated dictionary manages domain acronyms and terminology mappings:
- `VO2` $\rightarrow$ `VO2max`, `maximum oxygen uptake`
- `FTP` $\rightarrow$ `Functional Threshold Power`, `MLSS`, `Maximal Lactate Steady State`
- `TTE` $\rightarrow$ `Time to Exhaustion`
- `W_prime` / `W'` $\rightarrow$ `Anaerobic Work Capacity`
- `LT1` / `VT1` $\rightarrow$ `Aerobic Threshold`
- `LT2` / `VT2` $\rightarrow$ `Anaerobic Threshold`, `Second Threshold`

#### C. FTS5 BM25 Column Weighting
SQLite FTS5 provides a `bm25()` helper that accepts column weights:
$$\text{BM25\_Score} = \sum_{i \in \text{columns}} w_i \cdot \text{bm25}(i)$$

**Column Configuration:**
- `title`: `5.0` (Title matches indicate primary topic focus)
- `author`: `1.0`
- `category`: `2.0` (Matches against taxonomical category)
- `topics`: `4.0` (Curated topic tags)
- `section_path`: `2.0` (Markdown header breadcrumbs)
- `content`: `1.0` (Passage body text)

**SQL Query:**
```sql
SELECT
    p.chunk_id, s.title, p.start_line, p.end_line, p.content,
    bm25(passages_fts, 5.0, 1.0, 2.0, 4.0, 2.0, 1.0) AS lexical_rank
FROM passages_fts
JOIN passages p ON p.id = passages_fts.rowid
JOIN sources s ON s.id = p.source_id
WHERE passages_fts MATCH ?
ORDER BY lexical_rank ASC
LIMIT ?;
```

---

## 3. Agent Query Intelligence & MCP Routing

### Problem Statement
Athletes frequently ask complex, compound questions:
> *"How do I balance double threshold sessions with heavy torque strength training in a polarized block?"*

A single search query against this prompt will often match only one of the concepts.

### Design & Solution

#### A. Multi-Query Execution & Synthesis
`KBEngine` exposes `multi_search(queries: Sequence[str])`:
1. Executes independent searches for each sub-query.
2. Normalizes scores or merges candidate lists using rank reciprocal pooling.
3. Deduplicates passages by `chunk_id`.

#### B. MCP Server Tool Guidance
In `main/mcp_server.py`, the tool docstrings and descriptions provide structured instructions for the LLM:
- How to route queries to `category` (`metrics`, `hiit`, `zone2`, `strength`, `nutrition`, `physiology`, `periodization`).
- How to use canonical `topic` tags from `Knowledge_base/TAXONOMY.md`.
- Exposing `search_multi_passages` so LLMs can execute parallel sub-queries for multi-part questions.

---

## 4. Local Hybrid Search & Reciprocal Rank Fusion (RRF)

### Problem Statement
BM25 relies on exact lexical token matching. When an athlete asks about conceptual ideas without knowing the exact scientific terminology (e.g. *"how does low heart rate training make mitochondria grow"*), lexical search may score low if the passage uses *"mitochondrial biogenesis via AMPK phosphorylation"*.

### Design & Solution

#### A. Local Dense Embeddings
1. **Offline & Zero-Cloud Constraint**: Embeddings are computed locally using an embedded CPU model or lightweight local feature representations.
2. **Storage**: Vectors are managed alongside `.kb_index.sqlite`.
3. **Graceful Fallback**: If vector dependencies are not present, the engine automatically falls back to weighted BM25 without throwing errors.

#### B. Reciprocal Rank Fusion (RRF)
RRF is a robust, scale-invariant rank aggregation algorithm that combines rankings from multiple distinct retrieval models without needing calibrated probabilities or score normalization:

$$\operatorname{RRF}(d \in D) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$

Where:
- $M = \{\text{lexical\_bm25}, \text{dense\_vector}\}$
- $r_m(d)$ is the 1-based rank position of passage $d$ in model $m$.
- $k$ is the smoothing constant (default: $k = 60$).

**Algorithm Walkthrough:**
```python
def reciprocal_rank_fusion(
    bm25_results: list[EvidencePassage],
    dense_results: list[EvidencePassage],
    k: int = 60,
    top_n: int = 5,
) -> list[EvidencePassage]:
    scores: dict[str, float] = defaultdict(float)
    passage_map: dict[str, EvidencePassage] = {}

    # Accumulate sparse BM25 ranks
    for rank, passage in enumerate(bm25_results, start=1):
        scores[passage.chunk_id] += 1.0 / (k + rank)
        passage_map[passage.chunk_id] = passage

    # Accumulate dense vector ranks
    for rank, passage in enumerate(dense_results, start=1):
        scores[passage.chunk_id] += 1.0 / (k + rank)
        passage_map[passage.chunk_id] = passage

    # Sort descending by fused RRF score
    sorted_ids = sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)
    return [passage_map[cid] for cid in sorted_ids[:top_n]]
```

---

## 5. Evaluation Harness & Benchmark Specifications

To prove that improvements provide measurable gains over the baseline, the repository includes an automated evaluation harness: `main/benchmark.py` operating on `docs/prototypes/003-retrieval-benchmark.json`.

### Metrics Measured:
1. **MRR@5 (Mean Reciprocal Rank)**:
   $$\operatorname{MRR@5} = \frac{1}{|Q|} \sum_{q \in Q} \frac{1}{\operatorname{rank}_q}$$
2. **NDCG@5 (Normalized Discounted Cumulative Gain)**:
   Tests graded relevance ($3, 2, 1$).
3. **Recall@5**:
   Proportion of gold passages retrieved in top 5.
4. **Latency p95**:
   Query execution latency in milliseconds.

---

## 6. How to Build & Extend This Yourself

If you want to modify or expand this architecture:

1. **Domain Synonyms (`main/utils/kb_engine/synonyms.py`)**:
   - Add new domain keywords and synonyms to `DOMAIN_SYNONYMS`.
   - Update `STOP_WORDS` to filter additional conversational phrases.
2. **FTS5 Column Weights (`main/utils/kb_engine/fts.py`)**:
   - Adjust weights in `bm25(passages_fts, w1, w2, w3, w4, w5, w6)` to test different feature priorities.
3. **Benchmark Verification**:
   - Run `python3 main/benchmark.py` to compare performance.
4. **Unit Tests**:
   - Run `python3 -m unittest discover -s tests` to verify zero regressions across the test suite.
