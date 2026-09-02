---
title: 'Confronting Uncertainty in Training and Data: Bayesian Updating, Model Limits,
  and the Adaptive Coaching Loop — Complete Guide'
category: training
topics:
- Threshold_intervals
- VO2max_and_aerobic_hiit
- Biomechanics_fit_and_equipment
- Training_intensity_distribution
- Workload_quantification_and_modeling
- Tapering_and_peaking
- Psychology_and_cognitive_performance
source: 'Empirical Cycling Podcast — Kolie Moore & Gediminas (Watts Doc #63)'
author: Kolie Moore
date: '2026-04-29'
summary: The document discusses the application of Bayesian updating in training,
  emphasizing the importance of minimizing uncertainty through structured data collection
  and experiential feedback loops. It highlights the need for adaptive training plans
  and the use of threshold intervals and VO2max sessions to monitor and adjust training
  intensity.
key_takeaways:
- Athletic training is probabilistic, not algorithmic; deterministic training templates
  fail because individual responses are constrained by dynamic biological, environmental,
  and recovery factors.
- A single isolated test provides only moderate statistical confidence (a Bayesian
  posterior of ~68–75%); true confidence is built through iterative post-test interval
  verification.
- High test reliability (repeatability) does not equal high accuracy; a test contaminated
  by anaerobic capacity or protocol flaws can reliably produce an inaccurate threshold
  estimate.
- Embedding performance monitoring directly within regular training sessions ('testing
  is training and training is testing') reduces uncertainty without imposing high-stakes
  testing anxiety.
- The observation step in the scientific method (FAFO) is non-negotiable; coaches
  must avoid both dogmatic under-correction (ignoring athlete feedback) and erratic
  overcorrection (trend hopping).
---
# Confronting Uncertainty in Training and Data: Bayesian Updating, Model Limits, and the Adaptive Coaching Loop — Complete Guide
_Source: Empirical Cycling Podcast — Kolie Moore & Gediminas (Watts Doc #63)_

---

## What Is the Problem of Uncertainty in Training?

Endurance sports media often presents training as a deterministic algorithm: *"Execute Protocol $X$ for $Y$ weeks $\rightarrow$ guaranteed $+20\text{ Watts}$ FTP."* In reality, human physiology behaves far more like a probabilistic system operating under constant environmental, autonomic, and psychological noise.

```
Deterministic Fallacy vs. Probabilistic Reality:
 [Deterministic Belief]  Training Input (TSS/Intervals) ──► Guaranteed Output (+20W)
 
 [Probabilistic Reality] Training Input ──► [Biological Filter: Sleep, Life Stress, Genetics]
                                                │
                                                ▼
                                         Fuzzy Probability Distribution of Outcomes
```

Every workout, training block, and race plan is fundamentally a **forecast**. A coach or self-coached athlete's objective is to apply structured data collection and experiential feedback loops to progressively **minimize surprise** and reduce uncertainty over time.

---

## Key Physiological Mechanisms & Mathematical Frameworks

### 1. Bayesian Updating in Athletic Assessment

Bayes' Theorem provides a rigorous mathematical framework for how experienced coaches evaluate test data and update their beliefs about an athlete's true physiological capacity:

$$P(\text{True Gain} \mid \text{Test Result}) = \frac{P(\text{Test Result} \mid \text{True Gain}) \cdot P(\text{True Gain})}{P(\text{Test Result})}$$

```
                The Bayesian Assessment Loop:
 [Prior Probability P(Gain)]  (Base rate: ~10% for a random athlete gaining 20W)
              │
              ▼
 [Single Test Event]         (+20W recorded on field test)
              │
              ▼
 [Calculated Posterior]       (~68% confidence of true biological gain)
              │
              ▼
 [Iterative Training Data]    (3 subsequent workouts executed cleanly at new target)
              │
              ▼
 [Updated Final Posterior]    (>95% confidence; threshold ratified)
```

#### Step-by-Step Bayesian Calculation Example: A +20W FTP Field Test
* **Prior Belief $P(\text{Gain})$:** Across a generalized population of trained cyclists, what is the base rate probability of gaining $+20\text{W}$ of true threshold power over a single winter block? (Assigned conservatively at $\approx 0.10$ or $10\%$).
* **True Positive Rate $P(\text{Test} \mid \text{Gain})$:** If an athlete truly gained $20\text{W}$, how likely is a quality open-ended long test to detect it? ($\approx 0.95$ or $95\%$).
* **Marginal Likelihood $P(\text{Test})$:** The total probability of observing a $+20\text{W}$ test result across the population, including false positives (e.g., miscalibrated power meter, high-caffeine one-off day, excessive anaerobic surge): $\approx 0.14$.
* **The Single-Test Posterior:**
  $$P = \frac{0.95 \times 0.10}{0.14} \approx 67.8\%$$

> [!NOTE]
> A single isolated testing event yields only **~68% confidence** that a full $+20\text{W}$ physiological adaptation occurred. True certainty is established through subsequent training sessions where the new baseline is repeatedly operationalized.

---

### 2. Reliability vs. Accuracy in Training Data

A primary source of coaching error is conflating **reliability** (repeatability) with **accuracy** (fidelity to true physiology):

```
┌─────────────────────────┬───────────────────────────────────────────┬───────────────────────────────────────────┐
│ Metric Dimension        │ Scientific Definition                     │ Example in Cycling Power Testing          │
├─────────────────────────┼───────────────────────────────────────────┼───────────────────────────────────────────┤
│ **Reliability**         │ Consistency and reproducibility of a      │ A 20-minute test without a blowout effort │
│                         │ measurement across repeated trials        │ produces an ICC of 0.97 (highly reliable).│
├─────────────────────────┼───────────────────────────────────────────┼───────────────────────────────────────────┤
│ **Accuracy**            │ Degree of conformity between a measured   │ If the athlete has a 40 kJ anaerobic      │
│                         │ value and the true physiological state    │ capacity ($W'$), 95% of 20-min power      │
│                         │ (Maximal Lactate Steady State / MLSS)     │ overestimates true FTP by 25 Watts.       │
└─────────────────────────┴───────────────────────────────────────────┴───────────────────────────────────────────┘
```

A testing protocol can be exceptionally reliable (yielding the exact same number every Tuesday) while remaining fundamentally inaccurate if it captures non-target physiological systems (e.g., anaerobic work capacity biasing a short aerobic test).

---

### 3. The "Box of Models" & Modeling Traps

As statistician George Box famously stated: *"All models are wrong, but some are useful."* In endurance training, coaches interact with mathematical abstractions of reality:

* **Modeled Thresholds (mFTP, CP):** Mathematical approximations derived from power-duration curves. If the athlete has not performed an all-out effort in the 30–60 minute domain recently, the model's predictive accuracy collapses.
* **Training Load Algorithms (TSS, CTL, TRIMP):** Quantify external work volume and intensity weighting, but possess zero awareness of internal biological cost, autonomic stress, or glycogen depletion.
* **Laboratory Step Tests (4 mmol/L pins):** Assume fixed blood lactate concentrations represent identical metabolic states across all human fiber typologies, ignoring baseline shifts and baseline substrate utilization.

---

## Practical Application: The FAFO Adaptive Coaching Loop

The core scientific methodology—**FAFO ("Fucking Around and Finding Out")**—is the definitive operational loop for coaching and self-coaching:

```
                      The FAFO Adaptive Loop
  ┌─────────────────────────────────────────────────────────────┐
  │ 1. Formulate Hypothesis (e.g., "Extending TTE at 95% FTP   │
  │    will improve fatigue resistance in 3-hour road races")   │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 2. Execute Controlled Experiment (Prescribe 3-week micro-   │
  │    block: 3x15m → 2x25m → 2x30m; hold base volume constant) │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 3. THE SACRED OBSERVATION STEP (Track workout execution RPE, │
  │    decoupling, heart rate kinetics, and post-ride recovery) │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 4. Update Priors & Adjust (Ratify adaptation, extend TTE    │
  │    further, or pivot to VO2max if fractional ceiling is hit)│
  └─────────────────────────────────────────────────────────────┘
```

### Operational Rules for Embedded Field Tracking
1. **"Testing Is Training, Training Is Testing":** Rather than scheduling traumatic, high-stress testing weeks every 6 weeks, use regular interval progressions as continuous data probes. If an athlete completes $2 \times 25\text{ min}$ at target wattage with declining RPE and stable cardiovascular drift, threshold adaptation is confirmed.
2. **Standardize Environmental Baselines:** When benchmarking power, control for contextual confounders:
   * Bike position (Road vs. TT aerobars)
   * Terrain (Sustained gradient vs. flat vs. indoor trainer flywheel inertia)
   * Thermal stress (Indoor fan airflow / ambient temperature)
3. **Auto-Regulation over Rigid Compliance:** An athlete who recognizes severe autonomic fatigue and cuts a 4-hour ride to 90 minutes of Zone 1 provides vital biological feedback. Do not force compliance with a pre-planned spreadsheet when biological noise is screaming.

---

## Common Pitfalls & Limitations

```
Error Extremes in Coaching Decision Making:
 ┌─────────────────────────────────────────────────────────────────────────┐
 │ Under-Correction (Dogmatic Rigidity) ◄───────── IDEAL ─────────► Overcorrection (Dogma Hopping)
 ├──────────────────────────────────────┬─────────────────────────┬────────────────────────────────┤
 │ • Ignores negative athlete feedback  │ • Holds priors loosely  │ • Scraps entire training plan  │
 │ • Blames athlete for plan failure    │ • Changes 1 variable    │   after 1 bad workout          │
 │ • Re-runs failed blocks repeatedly   │ • Updates incrementally │ • Jumps between trends weekly  │
 └──────────────────────────────────────┴─────────────────────────┴────────────────────────────────┘
```

1. **Dogmatic Under-Correction:** Adhering to a rigid training template (e.g., traditional 3 weeks on / 1 week off) despite consistent athlete overreaching, blaming the athlete's work ethic rather than the model.
2. **Erratic Overcorrection (Trend Hopping):** Abandoning a productive aerobic base block because of a single sluggish weekend ride, immediately switching to extreme low-carb, polarized, or heavy torque models.
3. **Overvaluing Mechanistic Stories:** Believing a training method is superior purely because a paper demonstrated transient upstream molecular phosphorylation (e.g., PGC-1$\alpha$ mRNA spikes) without confirming sustained performance improvements.
4. **Confusing Race Results with Training Efficacy:** Assuming a poor race finish proves a training plan failed, while ignoring race dynamics (crashes, tactical mispositioning, flat tires, drafting dynamics).

---

## Summary Checklist / Decision Table

### Framework for Evaluating Training Feedback and Data Signals

| Signal / Observation | Bayesian Interpretation | Prescribed Coaching Action |
| :--- | :--- | :--- |
| **New peak FTP set during open-ended test (+15W)** | Prior confidence ~70%; requires operational verification | Prescribe standard threshold session ($2 \times 20\text{m}$) at new target; observe RPE |
| **Athlete fails target wattage on rep 2 of VO2max set** | Acute biological error (sleep debt, life stress) or under-recovery | Abort interval session immediately; convert to Zone 1 spin; audit sleep/fueling |
| **RPE drops from 8/10 to 6/10 across 4 weeks of Sweet Spot** | High-probability true aerobic adaptation | Nudge power target by $+5\text{ Watts}$ or extend duration by $+10\text{ minutes}$ |
| **Power numbers exceptional, but dropped in opening race** | Fitness model is accurate; tactical/positioning skill is limiting | Shift training focus to group rides, race simulation drills, and pack positioning |

### Coach & Athlete Uncertainty Checklist

* [ ] **Identify the Base Rate (Prior):** Establish realistic expectations based on the athlete's training age, historical progression, and biological age.
* [ ] **Isolate Single Variables:** When experimenting with a new stimulus (e.g., double threshold or high torque), keep base volume and off-bike variables stable.
* [ ] **Verify Test Outcomes:** Never adjust training zones permanently off a single outlier workout; confirm with 2–3 regular training sessions.
* [ ] **Maintain the Sacred Observation Step:** Systematically review athlete subjective comments, RPE, and post-session recovery markers alongside power files.
* [ ] **Embrace FAFO Incrementally:** Introduce novel training stimuli in small, measurable micro-doses before committing an entire multi-month block.
