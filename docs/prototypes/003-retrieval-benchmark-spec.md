# English Retrieval Benchmark and Candidate Acceptance Targets

**Document version:** 1.1.0

**Issue reference:** Issue #3, *Establish the retrieval benchmark and acceptance thresholds*

**Dataset artifact:** [`003-retrieval-benchmark.json`](003-retrieval-benchmark.json)

**Scope:** English-only, lexical and passage benchmark foundation

**Updated:** 2026-08-20

## 1. Purpose and current scope

This specification defines the English-only foundation for evaluating retrieval over the Endurance Training Knowledge Base. It first tests whether the system can create and retrieve the right citation-stable Evidence Passages: correct source identity, exact source lines, useful section context, deterministic passage boundaries, lexical ranking, and rejection of unsupported queries.

The dataset contains **9 Athlete Queries**:

- **7 positive queries** with **18 gold passage labels** across **16 unique English sources**.
- **2 negative queries** with no gold passage.
- **7 challenge categories**: broad planning, physiology, HIIT, Zone 2, strength, source conflicts, and unsupported-domain rejection.

This is not evidence that a semantic, dense-vector, hybrid, or reranking model meets any quality target. Every baseline and model result must come from a reproducible run against this dataset. Architecture choices and model reputation are not measurements.

The retained query IDs are `Q01`, `Q03`, `Q05`, `Q07`, `Q09`, `Q15`, `Q16`, `Q17`, and `Q18`.

## 2. Candidate acceptance targets

These values are **targets pending measurement**, not reported results. Positive-query ranking metrics are calculated over `Q01`, `Q03`, `Q05`, `Q07`, `Q09`, `Q15`, and `Q16`. Negative-query behavior is reported separately for `Q17` and `Q18`.

| Metric | Candidate target | Current measured baseline | Purpose |
| :--- | :--- | :--- | :--- |
| **MRR@5** | $\ge 0.85$ | Not yet measured | Rewards placing the first relevant Evidence Passage near the top. |
| **NDCG@5** | $\ge 0.80$ | Not yet measured | Tests graded ranking quality using relevance labels 3, 2, and 1. |
| **Recall@5** | $\ge 0.85$ | Not yet measured | Tests how many labelled gold passages appear in the first five results. |
| **Latency p95** | $< 500\text{ ms}$ | Not yet measured | Bounds query latency under a recorded hardware and cache configuration. |
| **Negative-query false positives** | $0$ | Not yet measured | Requires no result above the configured relevance threshold for unsupported queries. |

Targets may be revised after the harness, passage labels, and lexical baseline have been independently checked. Any revision must update both this specification and the JSON version.

## 3. Dataset inventory and gold mapping

The source line ranges below correspond to the current default `StructureAwareChunker` policy (`target_words=350`, `min_words=80`, `max_words=600`) and the corpus state inspected on 2026-08-20. Corpus changes must cause benchmark-integrity validation to fail until the gold ranges are reviewed.

### 3.1 Broad planning — Q01

**Query:** “How to increase my FTP over a 12-week block?”

- [`FTP_training.md#L15-L29`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/FTP_training.md#L15-L29), relevance 3.
- [`FTP_decision_tree.md#L39-L46`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/FTP_decision_tree.md#L39-L46), relevance 3.
- [`FTP_TTE_2.md#L17-L43`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/FTP_TTE_2.md#L17-L43), relevance 2.

### 3.2 Cardiac physiology — Q03

**Query:** “What physiological changes occur in cardiac stroke volume and cardiac hypertrophy from endurance training?”

- [`physiology-cyclists-key-muscle-heart.md#L16-L74`](../../Knowledge_base/Articles/knowledgeIsWatts/physiology/physiology-cyclists-key-muscle-heart.md#L16-L74), relevance 3.
- [`FTP_decision_tree.md#L18-L37`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/FTP_decision_tree.md#L18-L37), relevance 2.

### 3.3 HIIT comparison — Q05

**Query:** “Are 4x8 minute VO2max intervals more effective than 4x4 or 4x16 minute intervals?”

- [`hiit-4x8-vs-4x4-vs-4x16.md#L59-L104`](../../Knowledge_base/Articles/knowledgeIsWatts/hiit/hiit-4x8-vs-4x4-vs-4x16.md#L59-L104), relevance 3.
- [`hiit-short-vs-long-intervals-trained-cyclists.md#L73-L109`](../../Knowledge_base/Articles/knowledgeIsWatts/hiit/hiit-short-vs-long-intervals-trained-cyclists.md#L73-L109), relevance 2.

### 3.4 Zone 2 and aerobic base — Q07

**Query:** “Is Zone 2 training intrinsically superior to Zone 3 and Zone 4 for mitochondrial and aerobic adaptations?”

- [`zone2-not-intrinsically-better-than-higher-zones.md#L100-L159`](../../Knowledge_base/Articles/knowledgeIsWatts/zone2/zone2-not-intrinsically-better-than-higher-zones.md#L100-L159), relevance 3.
- [`zone2-role-in-endurance-sports.md#L94-L130`](../../Knowledge_base/Articles/knowledgeIsWatts/zone2/zone2-role-in-endurance-sports.md#L94-L130), relevance 3.
- [`Base_training.md#L19-L33`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/training/base/Base_training.md#L19-L33), relevance 2.

### 3.5 Strength integration — Q09

**Query:** “Should endurance cyclists perform unilateral or bilateral gym strength exercises?”

- [`strength-unilateral-vs-bilateral-for-cycling.md#L64-L103`](../../Knowledge_base/Articles/knowledgeIsWatts/strength/strength-unilateral-vs-bilateral-for-cycling.md#L64-L103), relevance 3.
- [`strength-endurance-cyclists-practical-guidelines.md#L17-L57`](../../Knowledge_base/Articles/knowledgeIsWatts/strength/strength-endurance-cyclists-practical-guidelines.md#L17-L57), relevance 3.

### 3.6 Source conflicts and competing context — Q15 and Q16

**Q15:** “Is FTP defined as 95% of 20-minute power or as Maximal Lactate Steady State (MLSS) with variable TTE?”

- [`FTP_test.md#L15-L27`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/metrics/FTP_test.md#L15-L27), relevance 3.
- [`FTP_training.md#L15-L29`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/FTP_training.md#L15-L29), relevance 3.
- [`metrics-does-ftp-represent-second-threshold.md#L16-L55`](../../Knowledge_base/Articles/knowledgeIsWatts/metrics/metrics-does-ftp-represent-second-threshold.md#L16-L55), relevance 2.

**Q16:** “Does splitting daily workload into Norwegian double threshold sessions yield superior aerobic adaptations compared to single long sessions when total work is equal?”

- [`training-aerobic-adaptations-daily-workload-split.md#L60-L100`](../../Knowledge_base/Articles/knowledgeIsWatts/training/threshold/training-aerobic-adaptations-daily-workload-split.md#L60-L100), relevance 3.
- [`training-double-threshold-days-stress-and-recovery.md#L110-L138`](../../Knowledge_base/Articles/knowledgeIsWatts/training/threshold/training-double-threshold-days-stress-and-recovery.md#L110-L138), relevance 3.
- [`Norwegian Singles Method Subthreshold.md#L200-L213`](<../../Knowledge_base/Books/Norwegian Singles Method Subthreshold.md#L200-L213>), relevance 2.

### 3.7 Unsupported-domain rejection — Q17 and Q18

- **Q17:** “What is the optimal carb loading protocol for elite sprint kayaking performance?” Gold: none.
- **Q18:** “How to implement a ketogenic diet for competitive open water swimming?” Gold: none.

## 4. Integrity checks before scoring

A benchmark run is invalid unless all of these checks pass:

1. Every query has `language: "en"`, a unique ID, a known category, and a valid relevance score.
2. Every gold `rel_path` resolves to a curated Markdown Knowledge Source inside `Knowledge_base/`.
3. Every `start_line` and `end_line` matches a passage produced by the recorded chunking policy.
4. Every `target_snippet`, after normalizing Markdown emphasis and whitespace, occurs within its declared source range.
5. Counts derived from the JSON match its `dataset_summary`.
6. The benchmark run records the repository commit, corpus digest, index digest, chunking policy, retrieval configuration, hardware, Python version, and cache state.

## 5. Scoring protocol

Run the lexical passage retriever first and publish that output as the baseline. Later sparse, dense, hybrid, or reranked configurations must use the same corpus state, passage set, filters, and top-five cutoff.

For each positive query:

1. Retrieve the top five Evidence Passages.
2. Match results by canonical source identity and gold passage identity or an explicitly documented overlap rule.
3. Compute MRR@5, NDCG@5, and Recall@5.
4. Record per-query rankings so aggregate scores remain auditable.

For each negative query, apply the system's configured relevance threshold and count returned passages as false positives. Report negative behavior separately; do not fold queries with no gold passages into positive-query MRR or Recall.

### Metric definitions

1. **MRR@5**

   $$\operatorname{MRR@5} = \frac{1}{|Q|}\sum_{q \in Q}\frac{1}{\operatorname{rank}_q}$$

   The reciprocal rank is zero when no relevant passage appears in the first five results.

2. **NDCG@5**

   $$\operatorname{DCG@5} = \sum_{i=1}^{5}\frac{2^{\operatorname{rel}_i}-1}{\log_2(i+1)}, \qquad \operatorname{NDCG@5} = \frac{\operatorname{DCG@5}}{\operatorname{IDCG@5}}$$

3. **Recall@5**

   $$\operatorname{Recall@5} = \frac{|\text{gold passages retrieved in the first five}|}{|\text{gold passages for the query}|}$$

4. **Latency p95**

   Measure end-to-end retrieval latency over repeated runs and report warm-cache and cold-cache results separately. Do not include one-time index construction in query latency.

## 6. Reporting rule

Every result must identify the exact configuration that produced it and link to raw per-query output. Use language such as “measured MRR@5 was 0.71 on commit …” rather than “the selected model exceeds the target.” No semantic, hybrid, or reranking claim is accepted without a reproducible measurement against this version of the benchmark.
