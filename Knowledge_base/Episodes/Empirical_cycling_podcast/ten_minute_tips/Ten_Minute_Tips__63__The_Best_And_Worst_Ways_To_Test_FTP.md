---
title: "Ten Minute Tips #63: The Best And Worst Ways To Test FTP — Complete Guide"
category: "metrics"
topics:
  - "FTP"
  - "CP"
  - "LT2_VT2"
source: "Empirical Cycling Podcast — Kolie Moore with Rory Porteous"
author: "Kolie Moore"
date: "2025-09-11"
summary: "A rigorous breakdown of 10 methods for testing and estimating FTP, analyzing the mathematical and physiological flaws of ramp tests, 20-minute formulas, blood lactate protocols, and detailing the Kolie Moore long-format test."
key_takeaways:
  - "FTP is a physiological state—the inflection point of metabolic stability—not a mathematical formula or a fixed fraction of a short effort."
  - "Ramp tests systematically overestimate FTP by an average of +17 to +18W (+7%), with individual errors reaching +45 to +50W for anaerobically gifted riders."
  - "The standard 20-minute test ($95%$) has an error window of 88% to 98% of true FTP; the 5-minute pre-test 'clearing' blowout introduces excessive test variability."
  - "Blood lactate lab testing is highly confounded by protocol design (step length, hydration, glycogen, baseline criteria); static markers like 4.0 mmol/L OBLA rarely equal true MLSS."
  - "The Kolie Moore long-format progression test (35–60+ min quasi-steady-state ramp) eliminates mathematical inference, teaches interoceptive RPE at threshold, and directly measures TTE."
---

# Ten Minute Tips #63: The Best And Worst Ways To Test FTP — Complete Guide
_Source: Empirical Cycling Podcast — Kolie Moore with Rory Porteous_

---

## What Is Functional Threshold Power (FTP)?

Functional Threshold Power (FTP) is the highest power output an athlete can sustain in a quasi-steady metabolic state where lactate production and clearance reach equilibrium. Below FTP, fatigue accumulates slowly (sustainable for 40–90+ minutes); above FTP, metabolic homeostasis breaks down, systemic acid-base balance destabilizes, and Time-to-Exhaustion (TTE) drops sharply to 10–25 minutes.

Because FTP is a physiological inflection point, estimating it through short-duration tests or algorithmic formulas introduces severe errors. This guide reviews the mechanisms, biases, and practical validity of the 10 most common FTP testing and estimation protocols.

---

## Key Physiological Mechanisms / How to Think About It

### 1. Anaerobic Work Capacity ($W'$) Contamination
* **The Mathematical Flaw of Short Tests:** Any effort under 30–40 minutes derives a significant fraction of its energy from substrate-level phosphorylation (anaerobic glycolysis and phosphocreatine breakdown).
* **The "Normalized Power / Anaerobic Buster" Phenotype:** Athletes with large anaerobic work capacities ($W'$) or high sprinting power ($P_{max}$) can generate massive short-duration numbers. Dividing short efforts (e.g., 5-min, 8-min, or ramp steps) by population-average divisors drastically inflates estimated FTP by 20–50+ watts.

### 2. Empirical Ramp Test Accuracy & Bias
Ramp tests calculate FTP as a fixed fraction (~75%) of the final 1-minute power step. Empirical data from field trials (Jim Arnold cohort and Empirical Cycling coaching datasets) demonstrate:
* **Mean Systematic Bias:** An average overestimation of **+17 to +18 watts (+7%)**.
* **Wide Limits of Agreement:** Individual errors range from **-11W to +50W**.
* **Population Distribution:** Only ~25–33% of riders land within an acceptable $\pm 10\text{W}$ window; the vast majority are severely overestimated.

```
                  [ Ramp Test / Short Effort Testing ]
                                    │
                                    ▼
       High Anaerobic Capacity ($W'$) & High VO2max Ceiling
                                    │
                                    ▼
              Calculates Inflated Theoretical FTP (+20–50W)
                                    │
                                    ▼
             Prescribed Threshold Intervals ($2\times 20$ min)
                                    │
                                    ▼
   Severe Glycolytic Acidosis / Premature Failure / Autonomic Burnout
```

---

## Analysis of the 10 FTP Testing & Estimation Methods

| # | Testing / Estimation Method | Mechanism / Formula | Physiological Validity & Pitfalls | Recommendation |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Short Duration % Formulations** | 85–90% of $2\times 8\text{m}$ or $\sim 80\%$ of 5m power. | **Fatal Flaw:** Heavily contaminated by $W'$; overestimates anaerobic athletes by 40–50W+. | ❌ **Do Not Use** |
| **2** | **Ramp Tests (e.g., Zwift/TR)** | $75\%$ of maximum 1-min power in a 1-min step ramp. | **Fatal Flaw:** Measures peak aerobic capacity and anaerobic tolerance; mean bias of +17W over true FTP. | ❌ **Do Not Use** |
| **3** | **Classic 20-Minute Test** | $95\%$ of 20-min average power. | **Moderate Flaw:** True ratio spans 88% to 98%. Anaerobic riders test too high; pure diesel riders test accurate/low. 5-min clearing effort adds erratic fatigue. | ⚠️ **Use with Caution** |
| **4** | **Time-in-Zone in Long Rides** | Accumulating 60–90+ min in Zone 4 across 6–8h. | **Misconception:** Intermittent surges allow micro-recoveries; does not prove higher steady-state FTP. | ❌ **Do Not Use as Test** |
| **5** | **Normalized Power (NP) from Races** | 4th-power algorithm weighting stochastic surges. | **Flaw:** High-surge criteriums inflate NP by 40–50W; technical cyclocross courses deflate NP by 50–100W. | ⚠️ **Contextual Only** |
| **6** | **Peak 60-Minute Race Power** | Best 60-min power from mass-start road race. | **Flaw:** Confounded by pack drafting, terrain, and surging. Only valid if performed as a solo steady-state effort. | ⚠️ **Contextual Only** |
| **7** | **Critical Power (CP) 2-Parameter** | Linear model using 3-min and 12-to-15-min max tests. | **Moderate Utility:** Mathematically sound for interpolation, but extrapolates threshold slightly high; requires multiple max-effort test days. | ⚠️ **Acceptable Alternative** |
| **8** | **Blood Lactate Lab Testing** | Step tests assessing 4.0 mmol/L (OBLA) or DMax. | **Flaw:** Sensitive to step length (3m vs 10m), hydration, glycogen, and lack of warmup; static 4.0 mmol/L rarely equals MLSS. | ⚠️ **Requires Strict Protocol** |
| **9** | **HRV DFA-$\alpha_1$ Threshold (0.75)** | Heart rate variability fractal scaling. | **Fatal Flaw:** High artifact sensitivity and poor day-to-day reproducibility; unreliable for training prescription. | ❌ **Do Not Use** |
| **10** | **Kolie Moore Long Progression Test** | 35–60+ min progressive quasi-steady-state ramp. | **Gold Standard:** Directly measures steady-state capacity without mathematical inference; determines exact TTE and trains RPE. | ✅ **Highly Recommended** |

---

## Practical Application: The Kolie Moore Long-Format Test

### 1. Test Architecture & Execution
The test is structured to guide the athlete across their metabolic threshold in a controlled, progressive manner:

```
[ Phase 1: Warmup & Acclimation ]
10–15 min @ Sweet Spot (~88–92% of estimated FTP)
       │
       ▼
[ Phase 2: Steady-State Target ]
15–20 min @ Estimated FTP (100% target power / comfortable hard)
       │
       ▼
[ Phase 3: Progressive Ramp / Open-Ended ]
Gradually increase power by 5–10W every 2–5 minutes until exhaustion (TTE reached)
```

* **Outcome:** The average power across the entire continuous block (Phases 1–3) represents true FTP; the elapsed duration represents individual **Time-to-Exhaustion (TTE)**.
* **Failure Condition:** If the athlete starts too hard and cannot sustain power past 20–25 minutes, true FTP is lower than the starting target.

### 2. Testing by RPE in Trained Athletes
For experienced athletes, formal test days can be replaced by auto-regulated training sessions:
* Execute a standard $2\times 20\text{m}$ or $3\times 15\text{m}$ threshold session.
* Pacing rule: Ride at the maximum sustainable power where legs feel stable, breathing is controlled (hyperventilation is absent), and RPE is 7–8/10.
* Average power across completed sets provides an accurate reflection of current operational FTP.

---

## Common Pitfalls & Limitations

* **Treating FTP Tests as Ego Contests:** Trying to achieve an artificially high wattage via short tests, leading to training prescriptions that cause overreaching.
* **Testing While Fatigued:** Testing on heavy legs reflects acute autonomic fatigue rather than true structural metabolic capacity.
* **Relying on Default Software eFTP Algorithms:** Accepting automatic FTP updates triggered by short 3- to 5-minute efforts in third-party software dashboards.

---

## Summary Checklist / Decision Table

| Athlete Goal / Context | Best Testing / Estimation Approach | Rationale |
| :--- | :--- | :--- |
| **Establishing baseline FTP & TTE** | Kolie Moore Progression Test (35–60 min). | Yields exact physiological threshold and TTE without mathematical guessing. |
| **Intermediate athlete in mid-season build** | Auto-regulated $2\times 20$ min or $3\times 15$ min by RPE. | Avoids testing fatigue; integrates threshold calibration directly into workouts. |
| **Suspected anaerobic phenotype / sprinter** | Strictly avoid ramp tests and 8-min tests; use long-format 40+ min testing. | Prevents +30–50W overestimation caused by large anaerobic capacity ($W'$). |
| **Ultra-distance / gravel endurance athlete** | Long-format continuous test to determine TTE (>60 min). | Identifies true metabolic endurance and fat oxidation fatigue resistance. |
| **Quick check for fitness maintenance in-season** | 10–15 min interval at known FTP; assess RPE and heart rate. | Quick diagnostic of residual systemic fatigue vs. freshness. |
