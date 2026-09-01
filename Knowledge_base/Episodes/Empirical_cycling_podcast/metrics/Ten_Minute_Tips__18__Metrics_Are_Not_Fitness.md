---
title: 'Ten Minute Tips #18: Metrics Are Not Fitness — Complete Guide'
category: physiology
topics:
- FTP_and_functional_metrics
- Critical_power_and_w_prime
- Thresholds_and_metabolic_domains
source: Empirical Cycling Podcast — Kolie Moore & Kyle Houston
author: Kolie Moore
date: '2022-01-29'
summary: Kolie Moore and Kyle Houston break down the critical difference between modeled metrics and biological fitness, explaining mathematical artifacts in FTP, Critical Power, W', and VLamax, while exposing common logical fallacies in performance tracking.
key_takeaways:
- Metrics are descriptive mathematical representations of data, not physical fitness itself; 'training to the metric' often creates artificial score increases without true physiological adaptation.
- Mathematical artifacts in CP/$W'$ and FTP/FRC models mean that when FTP increases, calculated $W'$ or FRC automatically decreases even when absolute anaerobic power (5s–90s) is completely unchanged.
- The Fallacy of Division treats population averages as individual truths (e.g., assuming MLSS is 4.0 mmol/L or FTP is exactly 75% of ramp peak power for everyone).
- The Fallacy of Composition incorrectly assumes that training methods successful for a single elite athlete will work universally across all athletes.
- 'Diagnose training limiters through performance outcomes: running out of energy before the finale indicates an aerobic limiter, while lacking kick in the final 200m indicates an anaerobic/sprint limiter.'
---

# Ten Minute Tips #18: Metrics Are Not Fitness — Complete Guide
_Source: Empirical Cycling Podcast — Kolie Moore & Kyle Houston_

---

## What Is the "Metrics Are Not Fitness" Problem?

Modern endurance cycling relies heavily on digital modeling software (WKO5, GoldenCheetah, Intervals.icu) and mathematical parameters ($\text{FTP}$, $\text{CP}$, $W'$, $\text{FRC}$, $\text{VLa}_{\max}$, $\text{CTL}$). 

The core issue occurs when athletes and coaches confuse the **mathematical representation** with the **biological reality**:
- **Teaching to the Test:** Optimizing workout design to artificially elevate a specific testing score (e.g., performing anaerobic training to boost a 20-minute power test or ramp test) without developing the underlying aerobic bioenergetics.
- **Metric Chasing & Mathematical Artifacts:** Panicking when modeled anaerobic metrics (such as $W'$ or FRC) decline on a dashboard, failing to recognize that this is often a mathematical consequence of a rising FTP floor rather than actual physiological loss.
- **Model Confounds:** Forgetting that all mathematical models (Critical Power, Power-Duration curves, 2-parameter models) make simplifying assumptions that break down when misapplied.

```
  ┌────────────────────────────────────────────────────────┐
  │                 Biological Reality                     │
  │  - Muscle fiber capillarization & mitochondrial flux   │
  │  - Cardiac stroke volume & plasma volume expansion     │
  │  - Substrate utilization (fat vs carbohydrate flux)    │
  └───────────────────────────┬────────────────────────────┘
                              │ Filtered through testing
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │             Mathematical Metric / Model                │
  │  - FTP / Critical Power (asymptote / baseline floor)   │
  │  - W' / FRC (integral of area above baseline)          │
  │  - VLamax (estimated glycolysis rate from Pmax & FTP)  │
  └────────────────────────────────────────────────────────┘
```

---

## Key Physiological Mechanisms / How to Think About It

### 1. The Mathematical Coupling of FTP/CP and $W'$/FRC
In two-parameter Critical Power ($\text{CP}$) and Functional Reserve Capacity ($\text{FRC}$) models, total work performed above the baseline threshold is modeled as a finite energetic reserve:

$$W(t) = \text{CP} \times t + W'$$

$$\text{Work Above Baseline} = \int (\text{Power}(t) - \text{FTP}) \, dt$$

- **The Shifting Floor Artifact:** When an athlete's aerobic fitness improves and FTP/CP increases, the "floor" of the equation rises. 
- **Mechanical Drop in $W'$ / FRC:** Because the area between the power curve and the higher baseline is mathematically reduced, software models will calculate a drop in $W'$ or FRC (e.g., from $17.5\text{ kJ}$ down to $13.0\text{ kJ}$).
- **Physiological Reality:** If the athlete's raw sprint and short-duration power (5s to 90s) is unchanged, their true anaerobic capacity has not degraded at all.

```
Power (W)
 ^
 │       /══════\  <-- Real Power-Duration Curve (Unchanged)
 │      /        \
 │─────/──────────\─────────────────────────  NEW Higher FTP (Higher Baseline)
 │    /  [Smaller] \  <-- Modeled W'/FRC shrinks mathematically!
 │───/──────────────\───────────────────────  OLD Lower FTP (Lower Baseline)
 │  /  [Larger W']   \
 └──────────────────────────────────────────► Duration
```

### 2. $\text{VLa}_{\max}$ Models and $\text{P}_{\max}$ Interaction
- Modeled maximal glycolytic rate ($\text{VLa}_{\max}$) calculations are driven primarily by maximal neuromuscular sprint power ($\text{P}_{\max}$) scaled against aerobic capacity ($\text{FTP}$ or $\dot{V}\text{O}_2\text{max}$).
- A higher $\text{P}_{\max}$ increases glycolytic flux rates. When an athlete develops a massive aerobic engine ($\text{FTP} > 400\text{W}$), modeled $\text{VLa}_{\max}$ or FRC may appear lower relative to body mass, yet their functional capacity to contest high-speed finishes remains intact.

### 3. Logical Fallacies in Exercise Physiology & Coaching

#### A. The Fallacy of Division (Population Average $\to$ Individual)
- **Definition:** Assuming that what is true for a population average is true for every individual within that group.
- **Example 1 — Blood Lactate at MLSS:** Scientific papers frequently cite $4.0\text{ mmol/L}$ as the average maximal lactate steady state. In reality, individual MLSS values range from $<3.0\text{ mmol/L}$ to $>5.5\text{ mmol/L}$ with significant standard deviation ($\pm 0.7–1.0\text{ mmol/L}$). Prescribing threshold at exactly $4.0\text{ mmol/L}$ misprescribes intensity for the majority of athletes.
- **Example 2 — Ramp Test Percentages:** Assuming FTP is exactly 75% of peak 1-minute ramp power across all riders, when individual reality spans 70% to 84% based on anaerobic work capacity.

#### B. The Fallacy of Composition (Individual $\to$ General Population)
- **Definition:** Assuming that because a specific training method or interval structure worked for one elite athlete, it must work for all athletes.
- **Application:** Copying a WorldTour professional's training regimen or an NCAA national champion's volume distribution ignores differing training histories, fiber compositions, and recovery constraints.

---

## Practical Application & Prescriptions

### 1. Diagnosing True Athlete Limiters

Coaches and self-coached athletes should diagnose training needs by evaluating race-specific failure modes rather than isolated dashboard numbers:

```
Athlete Failure Mode Diagnostic:

1. Did the athlete get dropped mid-race, on long climbs, or lose contact before the finale?
   └──► Diagnosis: AEROBIC LIMITER (FTP, TTE, Aerobic Base / Sub-LT1 Durability)
   └──► Action: Increase low-intensity volume (kJ) and progress threshold Time-in-Zone.

2. Did the athlete comfortably make the final group/breakaway, position correctly into the final 200m, but get out-sprinted by 3+ bike lengths?
   └──► Diagnosis: ANAEROBIC / NEUROMUSCULAR LIMITER (Pmax, RFD, W')
   └──► Action: Introduce maximal sprints, heavy resistance training, and short-interval anaerobic capacity work.
```

### 2. Guardrails for Metric Interpretation

| Metric / Tool | Common Misinterpretation | Physiological Ground Truth | Recommended Best Practice |
| :--- | :--- | :--- | :--- |
| **20-Minute Test** | "Taking 95% of 20-min power always equals FTP." | Anaerobic contribution varies significantly ($W'$ can inflate 20-min power). | Use extended testing protocols (35–50+ min) or assess steady-state lactate/RPE. |
| **Ramp Test** | "75% of peak 1-min power is exact threshold." | Highly anaerobic riders over-test; aerobic diesels under-test. | Use only as a rough starting benchmark or to evaluate maximal aerobic power. |
| **FRC / $W'$** | "A drop in FRC means I lost my sprint and punch." | FRC drops automatically when FTP increases due to model geometry. | Check absolute short-duration power (5s, 15s, 30s, 60s) before making training changes. |
| **Blood Lactate ($4.0\text{ mmol}$)** | "All athletes reach threshold at $4.0\text{ mmol/L}$." | Individual baseline and MLSS vary from 2.5 to 6.0 mmol/L. | Look for inflection points and stabilization curves over 20–30 min efforts. |

### 3. Balanced Seasonal Periodization
- **Sequential Priorities:** Avoid attempting to maximize all physiological capacities simultaneously (e.g., heavy strength training 3x/week + high-volume sweetspot + VO2max intervals).
- **Accept Planned Trade-Offs:** During aerobic/base development blocks, accept that maximal sprint and anaerobic reserves may remain stable or slightly suppressed while aerobic capacity expands.

---

## Common Pitfalls & Limitations

1. **Panic Retesting After Software Updates:**
   - Adjusting training zones downward simply because an algorithmic software update recalculated FRC or mFTP lower, without confirming field sensations.
2. **Conflating Testing Modalities:**
   - Comparing a 20-minute indoor test result against an outdoor road climb and treating the difference purely as fitness change rather than thermal, inertial, and biomechanical variation.
3. **Over-Measuring at the Expense of Consistency:**
   - Constantly scheduling testing sessions every 2–3 weeks to satisfy data tracking, disrupting cumulative progressive training blocks.
4. **Ignoring Hydration and Environmental Noise on Biomarkers:**
   - Relying on single-point blood lactate measurements without controlling for blood volume shifts, hydration state, prior carbohydrate depletion, or ambient temperature.

---

## Summary Checklist / Decision Table

```
Decision Flow: Interpreting Training Metrics & Testing Results
```

1. **Did a primary metric shift (e.g., FTP up, FRC down)?**
   - Verify raw power-duration points ($5\text{s}$, $30\text{s}$, $1\text{m}$, $5\text{m}$, $20\text{m}$, $40\text{m}$) before reacting to calculated summary metrics.
   - If short-duration power is stable while long-duration power increased, celebrate aerobic growth—do not attempt to "fix" FRC.

2. **Is a testing protocol being selected?**
   - **Ramp Test:** Acceptable for rapid benchmarking, but treat with caution for pacing long TTs or setting sweetspot zones.
   - **20-Minute Protocol:** Deduct 5% with caution; for anaerobic riders, 90–92% is often closer to true MLSS.
   - **Long-Duration TTE Test (35–60 min):** Gold standard for validating true sustained aerobic threshold.

3. **Are you applying population averages to your own training?**
   - Never assume fixed physiological constants (e.g. $4.0\text{ mmol/L}$ lactate, $220 - \text{age}$ max HR, $75\%$ ramp fraction).
   - Calibrate training zones to individual physiological markers, breathing transition points (VT1/VT2), and perceived exertion.
