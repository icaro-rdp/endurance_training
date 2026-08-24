# English Retrieval Benchmark and Candidate Acceptance Targets

**Document version:** 1.2.0

**Issue reference:** Issue #13, *Research and draft expanded gold retrieval benchmark dataset (30+ queries)*

**Dataset artifact:** [`003-retrieval-benchmark.json`](003-retrieval-benchmark.json)

**Scope:** English-only, lexical and passage benchmark foundation

**Updated:** 2026-08-24

## 1. Purpose and current scope

This specification defines the English-only foundation for evaluating retrieval over the Endurance Training Knowledge Base. It first tests whether the system can create and retrieve the right citation-stable Evidence Passages: correct source identity, exact source lines, useful section context, deterministic passage boundaries, lexical ranking, and rejection of unsupported queries.

The dataset contains **32 Athlete Queries**:

- **28 positive queries** with **59 gold passage labels** across **35 unique English sources**.
- **4 negative queries** with no gold passage.
- **7 core domain categories plus conflict and negative rejection**: broad planning, periodization, physiology, HIIT, Zone 2, strength, nutrition, metrics, source conflicts, and unsupported-domain rejection.

This is not evidence that a semantic, dense-vector, hybrid, or reranking model meets any quality target. Every baseline and model result must come from a reproducible run against this dataset. Architecture choices and model reputation are not measurements.

The dataset contains query IDs `Q01` through `Q32`.

## 2. Candidate acceptance targets

These values are **targets pending measurement**, not reported results. Positive-query ranking metrics are calculated over all 28 positive queries (`Q01`–`Q16`, `Q19`–`Q30`). Negative-query behavior is reported separately for `Q17`, `Q18`, `Q31`, and `Q32`.

| Metric | Candidate target | Current measured baseline | Purpose |
| :--- | :--- | :--- | :--- |
| **MRR@5** | $\ge 0.85$ | Not yet measured | Rewards placing the first relevant Evidence Passage near the top. |
| **NDCG@5** | $\ge 0.80$ | Not yet measured | Tests graded ranking quality using relevance labels 3, 2, and 1. |
| **Recall@5** | $\ge 0.85$ | Not yet measured | Tests how many labelled gold passages appear in the first five results. |
| **Latency p95** | $< 500\text{ ms}$ | Not yet measured | Bounds query latency under a recorded hardware and cache configuration. |
| **Negative-query false positives** | $0$ | Not yet measured | Requires no result above the configured relevance threshold for unsupported queries. |

Targets may be revised after the harness, passage labels, and lexical baseline have been independently checked. Any revision must update both this specification and the JSON version.

## 3. Dataset inventory and gold mapping

The source line ranges below correspond to the current default `StructureAwareChunker` policy (`target_words=350`, `min_words=80`, `max_words=600`) and the corpus state inspected on 2026-08-24. Corpus changes must cause benchmark-integrity validation to fail until the gold ranges are reviewed.

### 3.1 Broad planning — Q01

**Query:** “How to increase my FTP over a 12-week block?”

- [`FTP_training.md#L15-L29`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/FTP_training.md#L15-L29), relevance 3.
- [`FTP_decision_tree.md#L39-L46`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/FTP_decision_tree.md#L39-L46), relevance 3.
- [`FTP_TTE_2.md#L17-L43`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/FTP_TTE_2.md#L17-L43), relevance 2.

### 3.2 Periodization & Recovery Timelines — Q02, Q23, Q26, Q30

**Q02:** “Why testing FTP too soon after a VO2max block causes false failure?”

- [`1M__AMA.md#L63-L94`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/physiology/1M__AMA.md#L63-L94), relevance 3.

**Q23:** “How does a 6-day high-intensity interval shock microcycle followed by active recovery affect endurance performance?”

- [`training-high-intensity-shock-microcycle.md#L98-L140`](../../Knowledge_base/Articles/knowledgeIsWatts/training/vo2/training-high-intensity-shock-microcycle.md#L98-L140), relevance 3.
- [`training-high-intensity-shock-microcycle.md#L19-L56`](../../Knowledge_base/Articles/knowledgeIsWatts/training/vo2/training-high-intensity-shock-microcycle.md#L19-L56), relevance 2.

**Q26:** “How to raise time to exhaustion (TTE) at Functional Threshold Power without increasing target wattage?”

- [`FTP_TTE_2.md#L72-L86`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/FTP_TTE_2.md#L72-L86), relevance 3.
- [`FTP_training.md#L48-L63`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/FTP_training.md#L48-L63), relevance 3.

**Q30:** “How to combine heavy resistance strength training with high-intensity cycling interval microcycles without compromising recovery?”

- [`strength-endurance-cyclists-practical-guidelines.md#L95-L121`](../../Knowledge_base/Articles/knowledgeIsWatts/strength/strength-endurance-cyclists-practical-guidelines.md#L95-L121), relevance 3.
- [`strength-during-competition-period.md#L136-L167`](../../Knowledge_base/Articles/knowledgeIsWatts/strength/strength-during-competition-period.md#L136-L167), relevance 2.

### 3.3 Physiology & Hemodynamics — Q03, Q04, Q24

**Q03:** “What physiological changes occur in cardiac stroke volume and cardiac hypertrophy from endurance training?”

- [`physiology-cyclists-key-muscle-heart.md#L16-L74`](../../Knowledge_base/Articles/knowledgeIsWatts/physiology/physiology-cyclists-key-muscle-heart.md#L16-L74), relevance 3.
- [`FTP_decision_tree.md#L18-L37`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/FTP_decision_tree.md#L18-L37), relevance 2.

**Q04:** “How does the lactate shuttle transport lactate between fast-twitch and slow-twitch muscle fibers via MCT1 and MCT4?”

- [`Lactate_metabolism_and_shuttle.md#L48-L58`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/physiology/Lactate_metabolism_and_shuttle.md#L48-L58), relevance 3.
- [`Lactate_metabolism_and_shuttle.md#L59-L69`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/physiology/Lactate_metabolism_and_shuttle.md#L59-L69), relevance 3.

**Q24:** “How does ambient temperature affect maximal power output in male versus female professional road cyclists?”

- [`physiology-temperature-effect-on-performance-sex-differences.md#L67-L106`](../../Knowledge_base/Articles/knowledgeIsWatts/physiology/physiology-temperature-effect-on-performance-sex-differences.md#L67-L106), relevance 3.
- [`physiology-temperature-effect-on-performance-sex-differences.md#L53-L66`](../../Knowledge_base/Articles/knowledgeIsWatts/physiology/physiology-temperature-effect-on-performance-sex-differences.md#L53-L66), relevance 3.

### 3.4 High-Intensity Interval Training (HIIT) — Q05, Q06, Q25

**Q05:** “Are 4x8 minute VO2max intervals more effective than 4x4 or 4x16 minute intervals?”

- [`hiit-4x8-vs-4x4-vs-4x16.md#L59-L104`](../../Knowledge_base/Articles/knowledgeIsWatts/hiit/hiit-4x8-vs-4x4-vs-4x16.md#L59-L104), relevance 3.
- [`hiit-short-vs-long-intervals-trained-cyclists.md#L73-L109`](../../Knowledge_base/Articles/knowledgeIsWatts/hiit/hiit-short-vs-long-intervals-trained-cyclists.md#L73-L109), relevance 2.

**Q06:** “How do decreasing length intervals (HIDIT) optimize time spent above 90% VO2max compared to traditional long intervals?”

- [`hiit-optimizing-decreasing-length-intervals.md#L170-L205`](../../Knowledge_base/Articles/knowledgeIsWatts/hiit/hiit-optimizing-decreasing-length-intervals.md#L170-L205), relevance 3.
- [`hiit-optimizing-decreasing-length-intervals.md#L139-L169`](../../Knowledge_base/Articles/knowledgeIsWatts/hiit/hiit-optimizing-decreasing-length-intervals.md#L139-L169), relevance 3.

**Q25:** “Why does pedaling at higher cadence during VO2max intervals increase cardiac stroke volume and preload?”

- [`VO2_training.md#L57-L75`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/training/vo2/VO2_training.md#L57-L75), relevance 3.
- [`Fick_equation_and_cardiac_remodeling.md#L58-L74`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/physiology/Fick_equation_and_cardiac_remodeling.md#L58-L74), relevance 2.

### 3.5 Zone 2 and Aerobic Base — Q07, Q08, Q27

**Q07:** “Is Zone 2 training intrinsically superior to Zone 3 and Zone 4 for mitochondrial and aerobic adaptations?”

- [`zone2-not-intrinsically-better-than-higher-zones.md#L100-L159`](../../Knowledge_base/Articles/knowledgeIsWatts/zone2/zone2-not-intrinsically-better-than-higher-zones.md#L100-L159), relevance 3.
- [`zone2-role-in-endurance-sports.md#L94-L130`](../../Knowledge_base/Articles/knowledgeIsWatts/zone2/zone2-role-in-endurance-sports.md#L94-L130), relevance 3.
- [`Base_training.md#L19-L33`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/training/base/Base_training.md#L19-L33), relevance 2.

**Q08:** “How to estimate FatMax power and heart rate without a laboratory metabolic cart?”

- [`zone2-training-at-fatmax-without-lab.md#L96-L137`](../../Knowledge_base/Articles/knowledgeIsWatts/zone2/zone2-training-at-fatmax-without-lab.md#L96-L137), relevance 3.
- [`zone2-training-at-fatmax-without-lab.md#L20-L56`](../../Knowledge_base/Articles/knowledgeIsWatts/zone2/zone2-training-at-fatmax-without-lab.md#L20-L56), relevance 2.

**Q27:** “How does low intensity base endurance cycling stimulate cellular mitochondrial biogenesis?”

- [`1M__AMA.md#L46-L61`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/physiology/1M__AMA.md#L46-L61), relevance 3.
- [`Base_training.md#L19-L33`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/training/base/Base_training.md#L19-L33), relevance 2.

### 3.6 Strength Integration & Specificity — Q09, Q10, Q11, Q12

**Q09:** “Should endurance cyclists perform unilateral or bilateral gym strength exercises?”

- [`strength-unilateral-vs-bilateral-for-cycling.md#L64-L103`](../../Knowledge_base/Articles/knowledgeIsWatts/strength/strength-unilateral-vs-bilateral-for-cycling.md#L64-L103), relevance 3.
- [`strength-endurance-cyclists-practical-guidelines.md#L17-L57`](../../Knowledge_base/Articles/knowledgeIsWatts/strength/strength-endurance-cyclists-practical-guidelines.md#L17-L57), relevance 3.

**Q10:** “What happens to cycling power and muscle mass when strength training is stopped during the competition season?”

- [`strength-during-competition-period.md#L136-L167`](../../Knowledge_base/Articles/knowledgeIsWatts/strength/strength-during-competition-period.md#L136-L167), relevance 3.
- [`strength-during-competition-period.md#L49-L97`](../../Knowledge_base/Articles/knowledgeIsWatts/strength/strength-during-competition-period.md#L49-L97), relevance 3.

**Q11:** “Does high-intensity low-cadence torque training improve aerobic parameters more than free cadence cycling?”

- [`strength-high-intensity-torque-training.md#L82-L116`](../../Knowledge_base/Articles/knowledgeIsWatts/strength/strength-high-intensity-torque-training.md#L82-L116), relevance 3.
- [`strength-high-intensity-torque-training.md#L18-L46`](../../Knowledge_base/Articles/knowledgeIsWatts/strength/strength-high-intensity-torque-training.md#L18-L46), relevance 2.

**Q12:** “Is on-the-bike sprint training more effective than heavy gym squats for increasing peak 5-second sprint power?”

- [`training-improving-sprint-performance.md#L67-L91`](../../Knowledge_base/Articles/knowledgeIsWatts/training/strength/training-improving-sprint-performance.md#L67-L91), relevance 3.
- [`training-improving-sprint-performance.md#L48-L66`](../../Knowledge_base/Articles/knowledgeIsWatts/training/strength/training-improving-sprint-performance.md#L48-L66), relevance 2.

### 3.7 Sports Nutrition & Supplementation — Q13, Q14, Q19, Q20

**Q13:** “What is the recommended dosing and timing protocol for sodium bicarbonate supplementation before a race?”

- [`nutrition-sodium-bicarbonate-science-and-practical-use.md#L89-L123`](../../Knowledge_base/Articles/knowledgeIsWatts/nutrition/nutrition-sodium-bicarbonate-science-and-practical-use.md#L89-L123), relevance 3.
- [`nutrition-sodium-bicarbonate-science-and-practical-use.md#L124-L147`](../../Knowledge_base/Articles/knowledgeIsWatts/nutrition/nutrition-sodium-bicarbonate-science-and-practical-use.md#L124-L147), relevance 3.

**Q14:** “How does beta-alanine supplementation buffer muscle acidity and what is the optimal loading protocol for cyclists?”

- [`nutrition-beta-alanine-for-cycling.md#L95-L114`](../../Knowledge_base/Articles/knowledgeIsWatts/nutrition/nutrition-beta-alanine-for-cycling.md#L95-L114), relevance 3.
- [`nutrition-beta-alanine-for-cycling.md#L32-L45`](../../Knowledge_base/Articles/knowledgeIsWatts/nutrition/nutrition-beta-alanine-for-cycling.md#L32-L45), relevance 2.

**Q19:** “What glucose to fructose ratio should cyclists consume when carbohydrate intake exceeds 90 grams per hour?”

- [`nutrition-glucose-fructose-ratio.md#L60-L92`](../../Knowledge_base/Articles/knowledgeIsWatts/nutrition/nutrition-glucose-fructose-ratio.md#L60-L92), relevance 3.
- [`nutrition-glucose-fructose-ratio.md#L31-L59`](../../Knowledge_base/Articles/knowledgeIsWatts/nutrition/nutrition-glucose-fructose-ratio.md#L31-L59), relevance 2.

**Q20:** “Do high-dose antioxidant supplements like vitamin C and E blunt mitochondrial adaptations from endurance training?”

- [`nutrition-antioxidants-when-they-help-and-when-they-dont.md#L99-L112`](../../Knowledge_base/Articles/knowledgeIsWatts/nutrition/nutrition-antioxidants-when-they-help-and-when-they-dont.md#L99-L112), relevance 3.
- [`nutrition-antioxidants-when-they-help-and-when-they-dont.md#L113-L138`](../../Knowledge_base/Articles/knowledgeIsWatts/nutrition/nutrition-antioxidants-when-they-help-and-when-they-dont.md#L113-L138), relevance 2.

### 3.8 Performance Metrics & Fatigue Modeling — Q21, Q22

**Q21:** “What does the curvature constant W' represent in the Critical Power model and how is it depleted above CP?”

- [`metrics-estimating-cp-and-w-prime-best-individual-fit.md#L17-L70`](../../Knowledge_base/Articles/knowledgeIsWatts/metrics/metrics-estimating-cp-and-w-prime-best-individual-fit.md#L17-L70), relevance 3.
- [`metrics-critical-power-gold-standard-mss.md#L313-L342`](../../Knowledge_base/Articles/knowledgeIsWatts/metrics/metrics-critical-power-gold-standard-mss.md#L313-L342), relevance 3.

**Q22:** “How is durability or fatigue resistance measured in cycling after substantial energy expenditure?”

- [`metrics-measuring-durability-guide.md#L18-L59`](../../Knowledge_base/Articles/knowledgeIsWatts/metrics/metrics-measuring-durability-guide.md#L18-L59), relevance 3.
- [`metrics-measuring-durability-guide.md#L60-L139`](../../Knowledge_base/Articles/knowledgeIsWatts/metrics/metrics-measuring-durability-guide.md#L60-L139), relevance 3.

### 3.9 Source Conflicts & Nuanced Evidence — Q15, Q16, Q28, Q29

**Q15:** “Is FTP defined as 95% of 20-minute power or as Maximal Lactate Steady State (MLSS) with variable TTE?”

- [`FTP_test.md#L15-L27`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/metrics/FTP_test.md#L15-L27), relevance 3.
- [`FTP_training.md#L15-L29`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/FTP_training.md#L15-L29), relevance 3.
- [`metrics-does-ftp-represent-second-threshold.md#L16-L55`](../../Knowledge_base/Articles/knowledgeIsWatts/metrics/metrics-does-ftp-represent-second-threshold.md#L16-L55), relevance 2.

**Q16:** “Does splitting daily workload into Norwegian double threshold sessions yield superior aerobic adaptations compared to single long sessions when total work is equal?”

- [`training-aerobic-adaptations-daily-workload-split.md#L60-L100`](../../Knowledge_base/Articles/knowledgeIsWatts/training/threshold/training-aerobic-adaptations-daily-workload-split.md#L60-L100), relevance 3.
- [`training-double-threshold-days-stress-and-recovery.md#L110-L138`](../../Knowledge_base/Articles/knowledgeIsWatts/training/threshold/training-double-threshold-days-stress-and-recovery.md#L110-L138), relevance 3.

**Q28:** “Are fast-twitch muscle fibers purely anaerobic or can they develop high oxidative capacity through endurance training?”

- [`Watts_Doc__37__Your_Fast_Twitch_Fibers_Probably_As_Aerobic_As_Your_Slow_Twitch.md#L52-L73`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/physiology/Watts_Doc__37__Your_Fast_Twitch_Fibers_Probably_As_Aerobic_As_Your_Slow_Twitch.md#L52-L73), relevance 3.
- [`Watts_Doc__37__Your_Fast_Twitch_Fibers_Probably_As_Aerobic_As_Your_Slow_Twitch.md#L26-L47`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/physiology/Watts_Doc__37__Your_Fast_Twitch_Fibers_Probably_As_Aerobic_As_Your_Slow_Twitch.md#L26-L47), relevance 2.

**Q29:** “Do over-under intervals possess a unique physiological mechanism for lactate clearance compared to standard threshold intervals?”

- [`Over_unders.md#L32-L44`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/Over_unders.md#L32-L44), relevance 3.
- [`Over_unders.md#L18-L30`](../../Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/Over_unders.md#L18-L30), relevance 2.

### 3.10 Unsupported-Domain Rejection — Q17, Q18, Q31, Q32

- **Q17:** “What is the optimal carb loading protocol for elite sprint kayaking performance?” Gold: none.
- **Q18:** “How to implement a ketogenic diet for competitive open water swimming?” Gold: none.
- **Q31:** “What are the biomechanical efficiency advantages of barefoot forefoot running in marathon training?” Gold: none.
- **Q32:** “What is the optimal peaking microcycle for powerlifting bench press 1RM attempts?” Gold: none.