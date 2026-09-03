---
title: '143: Training Load Patterns and Quantification Models'
language: en
category: training
topics:
- Workload_quantification_and_modeling
- Microcycle_and_schedule_design
- Periodization_models_and_macrocycles
- Autonomic_and_cardiac_monitoring
- Overtraining_and_recovery_management
source: https://open.spotify.com/episode/4cbEu0eEEmRSL1rlxyGqKy
author: Daniele Bazzana, Stefano Nardelli
date: '2026-06-09'
summary: Compares major training load quantification models in endurance cycling—including Banister TRIMP, Coggan TSS, Foster session-RPE, and mechanical work—highlighting their underlying bioenergetic assumptions and clinical limitations.
---

# 143: Training Load Patterns and Quantification Models

## Overview and Physiological Definition

Quantifying training load is central to modern endurance coaching. It allows practitioners to plan progressive overload, model fitness and fatigue, avoid maladaptation, and time performance peaks. However, no single metric can capture the multifaceted biological stress of endurance exercise.

Training load models are broadly categorized into **external load metrics** (mechanical work performed on the bicycle) and **internal load metrics** (the physiological, cardiovascular, and psycho-perceptual strain experienced by the athlete). This episode critically examines the foundational quantification models used in cycling—Banister's TRIMP, Coggan's TSS/NP framework, Foster's session-RPE (sRPE), and raw mechanical energy expenditure (kJ)—and provides a framework for multi-metric load monitoring.

---

## 1. Analytical Comparison of Training Load Models

```
+-----------------------------------------------------------------------------------+
|                       TRAINING LOAD QUANTIFICATION MODELS                         |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [ MODEL ]              [ INPUT VARIABLES ]               [ PRIMARY BIAS / LIMIT ]|
|                                                                                   |
|  1. Banister TRIMP      HR Reserve (HRR), Duration,       Cardiovascular lag;     |
|                         Exponential Weighting Factor      Ignores neuromuscular  |
|                                                           and anaerobic strain    |
|                                                                                   |
|  2. Coggan TSS / NP     Normalized Power (4th power),     Over-indexes on FTP;   |
|                         Functional Threshold Power,       Equates 100 TSS HIIT   |
|                         Intensity Factor, Duration        to 100 TSS Zone 2       |
|                                                                                   |
|  3. Foster sRPE         Post-Session RPE (Borg CR10),     Subjective cognitive   |
|                         Session Duration (minutes)        bias; Non-linear with   |
|                                                           ultra-long durations    |
|                                                                                   |
|  4. Mechanical Work     Average Power (W), Duration (s)   Ignores intensity       |
|     (kJ / Total Work)   Total Energy Expended (kJ)        distribution and        |
|                                                           metabolic domains       |
+-----------------------------------------------------------------------------------+
```

### 1. Banister's TRIMP (Training Impulse)
- **Mathematical Basis:** Integrates duration ($t$) with fractional heart rate reserve ($\Delta\text{HR}$), weighted by an exponential factor ($y$) reflecting blood lactate accumulation:
  $$\text{TRIMP} = t \times \Delta\text{HR} \times 0.64e^{1.92 \Delta\text{HR}} \quad (\text{for males})$$
- **Strengths:** Directly captures internal cardiovascular strain and metabolic drift.
- **Limitations:** Heart rate response suffers from lag during short microbursts/sprints; fails to quantify neuromuscular force demands; influenced by ambient heat and dehydration.

### 2. Coggan's Training Stress Score (TSS) and Normalized Power (NP)
- **Mathematical Basis:** Weighting power output to the 4th power to account for physiological stress non-linearity above threshold:
  $$\text{TSS} = \frac{t \times \text{NP} \times \text{IF}}{\text{FTP} \times 3600} \times 100$$
- **Strengths:** Excellent standardization of external mechanical work relative to an athlete's functional capacity.
- **Limitations:** The **"TSS Equivalence Fallacy"**—100 TSS generated via 60 minutes of all-out VO2max intervals induces vastly different autonomic and endocrine fatigue than 100 TSS accumulated via 2.5 hours of low-intensity Zone 2 base riding.

### 3. Foster's Session-RPE (sRPE)
- **Mathematical Basis:** $\text{sRPE Load} = \text{Session Duration (min)} \times \text{Session RPE (Borg 0--10 Scale)}$.
- **Strengths:** Captures systemic, psychological, and musculoskeletal strain without requiring power meters or heart rate monitors.
- **Limitations:** High intra-individual variance; less precise for micro-interval management.

---

## 2. The Performance Management Chart (PMC) and Impulse-Response Modeling

The classical **Banister Impulse-Response Model** models performance as the difference between accumulated Fitness and accumulated Fatigue:

$$\text{Performance}(t) = k_1 \sum \text{Load} \cdot e^{-(t-\tau)/\tau_1} - k_2 \sum \text{Load} \cdot e^{-(t-\tau)/\tau_2}$$

In modern software (TrainingPeaks, WKO5), this is implemented via:
- **Chronic Training Load (CTL / Fitness):** Exponentially weighted moving average of daily load over ~42 days.
- **Acute Training Load (ATL / Fatigue):** Exponentially weighted moving average of daily load over ~7 days.
- **Training Stress Balance (TSB / Form):** $\text{TSB} = \text{CTL} - \text{ATL}$.

```
                 [ Chronic Training Load (CTL) - 42d ]
                                 -
                  [ Acute Training Load (ATL) - 7d ]
                                 =
                [ Training Stress Balance (TSB / Form) ]
                                 |
         +-----------------------+-----------------------+
         |                                               |
   TSB < -25 to -30                                TSB > +15 to +25
(High Overreaching / Injury Risk)              (Peaked but Detraining Risk)
```

### Critical Coaching Insights on PMC Usage
1. **CTL Is Not Fitness:** CTL represents accumulated historical training volume; it does not reflect metabolic adaptations, anaerobic threshold improvements, or cycling economy.
2. **The Ramp Rate Rule:** Increasing CTL faster than 5–8 TSS/day per week significantly elevates injury and non-functional overreaching risk.
3. **Tapering Dynamics:** Optimal race performance typically occurs when TSB is positive (+10 to +25), but prolonged positive TSB leads to loss of plasma volume and aerobic deconditioning.

---

## 3. Designing a Composite Load Monitoring Framework

Relying on a single metric creates diagnostic blind spots. A robust monitoring architecture cross-references external and internal indicators:

| Monitoring Tier | Primary Metrics | Diagnostic Objective |
| :--- | :--- | :--- |
| **Tier 1: External Volume & Work** | Mechanical Work (kJ), Duration (h) | Quantify total energetic throughput and fuel requirement |
| **Tier 2: Intensity & Threshold Stress** | Normalized Power, IF, Time-in-Zone | Monitor mechanical strain across specific metabolic domains |
| **Tier 3: Internal Cardiovascular Load** | hrTRIMP, Mean HR, $Pw:HR$ Decoupling | Detect cardiovascular drift and autonomic stress |
| **Tier 4: Psychobiological State** | Session-RPE, Morning Readiness (HRV, Soreness) | Detect central fatigue and non-functional overreaching |

---

## Key Takeaways and Practical Recommendations

- **Beware the TSS Fallacy:** 100 TSS from high-intensity anaerobic work has a completely different recovery timeline than 100 TSS from steady Zone 2 base miles.
- **Use Kilojoules for Fueling and Volume:** Kilojoules (kJ) provide an absolute, unmanipulated measurement of mechanical work that directly correlates with caloric expenditure and metabolic throughput.
- **Monitor the Internal-to-External Ratio:** An escalating heart-rate-to-power ratio ($Pw:HR$ decoupling) or rising session-RPE at standard training watts signals accumulated systemic fatigue.
- **Control CTL Ramp Rates:** Limit weekly CTL increases to 5–8 points per week during build phases to allow connective tissue, cardiovascular, and metabolic systems to adapt synchronously.
