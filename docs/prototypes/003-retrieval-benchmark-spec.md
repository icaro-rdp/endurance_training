# Retrieval Benchmark & Acceptance Threshold Specification

**Document Version:** 1.0.0  
**Issue Reference:** [Issue #3: Establish the retrieval benchmark and acceptance thresholds](file:///Users/icaroredepaolini/Personale/training/endurance_training/docs/agents/issue-tracker.md)  
**Author:** Endurance Research Team  
**Dataset Artifact:** [`docs/prototypes/003-retrieval-benchmark.json`](file:///Users/icaroredepaolini/Personale/training/endurance_training/docs/prototypes/003-retrieval-benchmark.json)  

---

## 1. Executive Summary

This specification establishes the official retrieval evaluation benchmark and quantitative acceptance contract for the **Endurance Training Knowledge Base**. To move beyond simple full-text keyword matching (SQLite FTS5 BM25), the retrieval system must prove robust accuracy across multi-lingual terminology (English and Italian), broad periodization planning, fine-grained exercise physiology, high-intensity interval training (HIIT), Zone 2 / aerobic base paradigms, gym strength integration, cross-lingual querying, scientific source conflicts, and negative out-of-domain query rejection.

The accompanying dataset [`003-retrieval-benchmark.json`](file:///Users/icaroredepaolini/Personale/training/endurance_training/docs/prototypes/003-retrieval-benchmark.json) contains **20 curated Athlete Queries** mapped to gold target passages across primary sources in `Knowledge_base/`.

---

## 2. Quantitative Acceptance Thresholds

The retrieval engine will be evaluated against five core performance metrics. Any proposed architecture (e.g., hybrid vector-BM25 search, cross-encoder reranking, metadata filtering) must meet or exceed the following minimum acceptance thresholds:

| Metric | Target Threshold | Baseline BM25 | Rationale & Description |
| :--- | :--- | :--- | :--- |
| **MRR@5** | $\ge \mathbf{0.85}$ | ~0.55 | **Mean Reciprocal Rank at Top 5**: Measures how quickly the top relevant gold passage is returned. Essential for immediate LLM context window insertion. |
| **NDCG@5** | $\ge \mathbf{0.80}$ | ~0.48 | **Normalized Discounted Cumulative Gain at Top 5**: Evaluates rank quality using graded relevance weights ($3 = \text{Primary Gold}$, $2 = \text{Secondary}$, $1 = \text{Marginal}$). |
| **Recall@5** | $\ge \mathbf{0.85}$ | ~0.50 | **Recall at Top 5**: Proportion of all gold relevant passages retrieved within the top 5 positions. Ensures full context capture. |
| **Latency (p95)** | $\mathbf{< 500\text{ ms}}$ | ~15 ms | **95th Percentile Query Latency**: Enforces production-grade responsiveness for real-time athlete interaction. |
| **Negative Query FP** | $\mathbf{0\text{ false positives}}$ | ~2 false positives | **Out-of-Domain Precision**: Ensures zero gold passage matches are hallucinated for non-endurance/unsupported queries (e.g., kayaking, swimming keto, tennis elbow). |

---

## 3. Query Dataset Taxonomy & Gold Mapping

The 20 benchmark queries are categorized into 8 functional retrieval challenges:

### 3.1 Broad Planning (Queries Q01, Q02)
- **Q01 (EN):** *"How to increase my FTP over a 12-week block?"*
  - **Gold Evidence:** [`FTP_training.md#L21-L60`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/FTP_training.md#L21-L60) (Score 3), [`FTP_decision_tree.md#L24-L53`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/FTP_decision_tree.md#L24-L53) (Score 3), [`FTP_TTE_2.md#L1-L40`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/FTP_TTE_2.md#L1-L40) (Score 2).
- **Q02 (IT):** *"Come strutturare la periodizzazione dell'allenamento per aumentare la potenza di soglia?"*
  - **Gold Evidence:** [`Periodizzazione dell'allenamento sportivo.md#L21-L32`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Books/Periodizzazione%20dell%27allenamento%20sportivo.md#L21-L32) (Score 3), [`FTP_training.md#L21-L60`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/FTP_training.md#L21-L60) (Score 3), [`training-high-intensity-shock-microcycle.md#L198-L240`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Articles/knowledgeIsWatts/training/vo2/training-high-intensity-shock-microcycle.md#L198-L240) (Score 2).

### 3.2 Specific Physiology (Queries Q03, Q04)
- **Q03 (EN):** *"What physiological changes occur in cardiac stroke volume and cardiac hypertrophy from endurance training?"*
  - **Gold Evidence:** [`physiology-cyclists-key-muscle-heart.md#L21-L60`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Articles/knowledgeIsWatts/physiology/physiology-cyclists-key-muscle-heart.md#L21-L60) (Score 3), [`FTP_decision_tree.md#L24-L33`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/FTP_decision_tree.md#L24-L33) (Score 2).
- **Q04 (IT):** *"Qual è il ruolo dei tamponi come il bicarbonato di sodio nel gestire l'accumulo di ioni idrogeno ad alta intensità?"*
  - **Gold Evidence:** [`nutrition-bicarbonate-boost-for-final-race-efforts.md#L24-L40`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Articles/knowledgeIsWatts/nutrition/nutrition-bicarbonate-boost-for-final-race-efforts.md#L24-L40) (Score 3), [`nutrition-bicarbonate-before-hit-boosts-adaptations.md#L162-L185`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Articles/knowledgeIsWatts/nutrition/nutrition-bicarbonate-before-hit-boosts-adaptations.md#L162-L185) (Score 3).

### 3.3 HIIT & Interval Design (Queries Q05, Q06)
- **Q05 (EN):** *"Are 4x8 minute VO2max intervals more effective than 4x4 or 4x16 minute intervals?"*
  - **Gold Evidence:** [`hiit-4x8-vs-4x4-vs-4x16.md#L71-L100`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Articles/knowledgeIsWatts/hiit/hiit-4x8-vs-4x4-vs-4x16.md#L71-L100) (Score 3), [`hiit-short-vs-long-intervals-trained-cyclists.md#L95-L120`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Articles/knowledgeIsWatts/hiit/hiit-short-vs-long-intervals-trained-cyclists.md#L95-L120) (Score 2).
- **Q06 (IT):** *"Come programmare gli intervalli brevi ad alta intensità con sovraccarico progressivo?"*
  - **Gold Evidence:** [`hiit-short-intervals-with-progressive-overload.md#L83-L120`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Articles/knowledgeIsWatts/hiit/hiit-short-intervals-with-progressive-overload.md#L83-L120) (Score 3).

### 3.4 Zone 2 & Aerobic Base (Queries Q07, Q08)
- **Q07 (EN):** *"Is Zone 2 training intrinsically superior to Zone 3 and Zone 4 for mitochondrial and aerobic adaptations?"*
  - **Gold Evidence:** [`zone2-not-intrinsically-better-than-higher-zones.md#L116-L150`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Articles/knowledgeIsWatts/zone2/zone2-not-intrinsically-better-than-higher-zones.md#L116-L150) (Score 3), [`zone2-role-in-endurance-sports.md#L108-L135`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Articles/knowledgeIsWatts/zone2/zone2-role-in-endurance-sports.md#L108-L135) (Score 3), [`Base_training.md#L200-L240`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Episodes/Empirical_cycling_podcast/training/base/Base_training.md#L200-L240) (Score 2).
- **Q08 (IT):** *"Come stimare l'intensità di FatMax senza un test di laboratorio con metabolimetro?"*
  - **Gold Evidence:** [`zone2-training-at-fatmax-without-lab.md#L112-L145`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Articles/knowledgeIsWatts/zone2/zone2-training-at-fatmax-without-lab.md#L112-L145) (Score 3).

### 3.5 Gym Strength Integration (Queries Q09, Q10)
- **Q09 (EN):** *"Should endurance cyclists perform unilateral or bilateral gym strength exercises?"*
  - **Gold Evidence:** [`strength-unilateral-vs-bilateral-for-cycling.md#L141-L175`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Articles/knowledgeIsWatts/strength/strength-unilateral-vs-bilateral-for-cycling.md#L141-L175) (Score 3), [`strength-endurance-cyclists-practical-guidelines.md#L137-L165`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Articles/knowledgeIsWatts/strength/strength-endurance-cyclists-practical-guidelines.md#L137-L165) (Score 3).
- **Q10 (IT):** *"È consigliabile continuare l'allenamento della forza in palestra durante il periodo agonistico o di gara?"*
  - **Gold Evidence:** [`strength-during-competition-period.md#L129-L155`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Articles/knowledgeIsWatts/strength/strength-during-competition-period.md#L129-L155) (Score 3).

### 3.6 Cross-Lingual Retrieval (Queries Q11, Q12, Q13, Q14)
- **Q11 (EN $\rightarrow$ IT):** *"What are Tudor Bompa's periodization phases for converting maximal strength into specific athletic endurance?"*
  - **Gold Evidence:** [`Periodizzazione dell'allenamento sportivo.md#L21-L32`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Books/Periodizzazione%20dell%27allenamento%20sportivo.md#L21-L32) (Score 3).
- **Q12 (EN $\rightarrow$ IT):** *"How does muscular adaptation progress through anatomical adaptation and hypertrophy according to Italian periodization literature?"*
  - **Gold Evidence:** [`Periodizzazione dell'allenamento sportivo.md#L21-L32`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Books/Periodizzazione%20dell%27allenamento%20sportivo.md#L21-L32) (Score 3).
- **Q13 (IT $\rightarrow$ EN):** *"Quali sono i vantaggi dell'allenamento a basso numero di pedalate ad alta coppia torsionale (heavy torque training)?"*
  - **Gold Evidence:** [`strength-high-intensity-torque-training.md#L125-L160`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Articles/knowledgeIsWatts/strength/strength-high-intensity-torque-training.md#L125-L160) (Score 3).
- **Q14 (IT $\rightarrow$ EN):** *"Perché la regola della potenza su un'ora per la FTP è fuorviante rispetto al Time to Exhaustion (TTE)?"*
  - **Gold Evidence:** [`FTP_TTE.md#L224-L260`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/FTP_TTE.md#L224-L260) (Score 3).

### 3.7 Scientific Source Conflicts & Debates (Queries Q15, Q16)
- **Q15 (EN):** *"Is FTP defined as 95% of 20-minute power or as Maximal Lactate Steady State (MLSS) with variable TTE?"*
  - **Gold Evidence:** [`FTP_test.md#L38-L70`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Episodes/Empirical_cycling_podcast/testing/FTP_test.md#L38-L70) (Score 3), [`FTP_training.md#L21-L45`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/FTP_training.md#L21-L45) (Score 3).
- **Q16 (EN):** *"Does splitting daily workload into Norwegian double threshold sessions yield superior aerobic adaptations compared to single long sessions when total work is equal?"*
  - **Gold Evidence:** [`training-aerobic-adaptations-daily-workload-split.md#L244-L270`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Articles/knowledgeIsWatts/training/threshold/training-aerobic-adaptations-daily-workload-split.md#L244-L270) (Score 3), [`training-double-threshold-days-stress-and-recovery.md#L208-L235`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Articles/knowledgeIsWatts/training/threshold/training-double-threshold-days-stress-and-recovery.md#L208-L235) (Score 3).

### 3.8 Negative / Out-of-Domain (Queries Q17, Q18, Q19, Q20)
- **Q17 (EN):** *"What is the optimal carb loading protocol for elite sprint kayaking performance?"* (Gold: None)
- **Q18 (EN):** *"How to implement a ketogenic diet for competitive open water swimming?"* (Gold: None)
- **Q19 (IT):** *"Quali sono le tecniche di ipertrofia muscolare per il bodybuilding naturale?"* (Gold: None)
- **Q20 (IT):** *"Come prevenire l'infortunio al gomito del tennista nel tennis amatoriale?"* (Gold: None)

---

## 4. Evaluation Architecture & Benchmark Harness

To execute this benchmark programmatically, a evaluation script will load [`docs/prototypes/003-retrieval-benchmark.json`](file:///Users/icaroredepaolini/Personale/training/endurance_training/docs/prototypes/003-retrieval-benchmark.json) and query `main/cli.py search`.

### Mathematical Metric Definitions

1. **Mean Reciprocal Rank (MRR@5)**:
   $$\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$$
   where $\text{rank}_i$ is the position of the first relevant gold passage returned (set to $\infty$ if not in top 5).

2. **Normalized Discounted Cumulative Gain (NDCG@5)**:
   $$\text{DCG}_k = \sum_{i=1}^{k} \frac{2^{\text{rel}_i} - 1}{\log_2(i + 1)}, \quad \text{NDCG}_k = \frac{\text{DCG}_k}{\text{IDCG}_k}$$
   where $\text{rel}_i$ is the gold relevance score ($0, 1, 2, 3$).

3. **Recall@5**:
   $$\text{Recall@5} = \frac{|\text{Retrieved Gold Passages in Top 5}|}{|\text{Total Gold Passages for Query}|}$$

---

## 5. Decision & Next Steps

1. Benchmark specification and JSON target dataset locked under [`docs/prototypes/`](file:///Users/icaroredepaolini/Personale/training/endurance_training/docs/prototypes/).
2. Issue #3 assigned to `icaro-rdp` and marked closed with this specification reference.
3. Subsequent work (e.g. dense vector embeddings, hybrid fusion, cross-encoder reranking) will use this benchmark to validate retrieval quality improvements against the baseline.
