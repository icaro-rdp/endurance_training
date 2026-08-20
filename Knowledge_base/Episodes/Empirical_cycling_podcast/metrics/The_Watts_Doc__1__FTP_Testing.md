---
title: "FTP Testing Protocols, Pitfalls, & Pacing — Complete Guide"
category: "metrics"
topics:
  - "FTP"
  - "TTA_TTE"
  - "W_prime"
source: "Empirical Cycling Podcast — Kolie Moore & Kyle Hanson (Watts Doc #1)"
author: "Kolie Moore"
date: "2019-03-24"
summary: "A comprehensive critical evaluation of FTP testing protocols (20-minute, 2x8-minute, ramp tests, and continuous long tests), detailing the confounding role of anaerobic work capacity (W'), Time-to-Exhaustion (TTE) dynamics, and precise field testing execution."
key_takeaways:
  - "FTP is the quasi-steady-state power sustainable without rapid fatigue, not an arbitrary 60-minute maximum effort."
  - "Short tests (8-minute, ramp tests, and 20-minute tests without a blowout) systematically overestimate FTP by capturing anaerobic work capacity (W')."
  - "Time to Exhaustion (TTE) at FTP varies significantly among athletes (typically 35 to 80+ minutes) and increases with aerobic training."
  - "Longer, progressive, open-ended tests (35–70+ minutes) provide an accurate measurement of true FTP and TTE while generating actionable power-duration inflection data."
---

# FTP Testing Protocols, Pitfalls, & Pacing — Complete Guide
_Source: Empirical Cycling Podcast — Kolie Moore & Kyle Hanson (Watts Doc #1)_

---

## What Is Functional Threshold Power (FTP)?

Functional Threshold Power (FTP) is one of the most widely used and misunderstood metrics in endurance cycling. Originally conceptualized by Dr. Andrew Coggan, FTP is defined as:

> **The highest power a rider can maintain in a quasi-steady state for approximately one hour without fatiguing.**

### The "60-Minute Power" Misconception
A widespread misconception in the cycling community is that FTP is strictly equivalent to an athlete's maximal 60-minute power output. Physiologically, there is nothing special or hardcoded in human physiology about 60 minutes:

* **Quasi-Steady State:** FTP represents the metabolic boundary where lactate production matches maximal rate of lactate clearance (Maximal Lactate Steady State / MLSS).
* **Time-to-Exhaustion (TTE):** The duration an athlete can sustain their exact FTP before task failure is not a fixed 60 minutes. Depending on training status, aerobic base, and fiber type distribution, TTE at FTP generally ranges from **35 to 80+ minutes**.
* **Trainability of TTE:** As an athlete develops aerobic fitness, their FTP wattage may stabilize while their TTE extends significantly (e.g., from 40 minutes out to 75 minutes), reflecting increased fatigue resistance and muscular endurance.

---

## Key Physiological Mechanisms / How to Think About It

```
      Total Power Output during Short Tests
 ┌──────────────────────────────────────────────┐
 │ Aerobic Contribution (Oxidative Flux)        │
 ├──────────────────────────────────────────────┤
 │ Anaerobic Contribution (W' / Glycolysis)     │ ◄── Overestimates FTP in short tests!
 └──────────────────────────────────────────────┘
```

### The Anaerobic Confounder ($W'$ / FRC Contribution)
Every athlete possesses a finite reservoir of work that can be performed above threshold, termed **$W'$** (W-prime) or **Functional Reserve Capacity (FRC)**. This energy is generated through substrate-level phosphorylation (phosphocreatine breakdown and fast anaerobic glycolysis).

* **Duration vs. Contribution:** In short testing durations (such as 8 minutes or 20 minutes), energy from $W'$ represents a significant fraction of total work performed.
* **The "Vanity FTP" Trap:** Athletes with high anaerobic capacity, fast-twitch fiber distribution, or sprint backgrounds can generate massive wattage during short protocols. Applying standard percentage reductions (e.g., 95% of 20-minute power) yields a mathematically inflated "vanity FTP" that does not reflect sustainable aerobic quasi-steady-state power.
* **Rider Phenotypes:**
  * **Anaerobic/Punchy Riders:** FTP may only represent **88% to 92%** of 20-minute power.
  * **Aerobic/Diesel Riders:** FTP may represent **96% to 98%** of 20-minute power.

### Perceptual & Neuromuscular Characteristics of Riding at FTP
Riding at true FTP has distinct physiological and perceptual markers:

* **Rate of Perceived Exertion (RPE):** Approximately **6 to 7 out of 10** on a standard RPE scale (or 14–16 on the 6–20 Borg scale). It feels like a sustainable "slow burn," not an immediate gasping crisis.
* **Ventilatory Control:** Ventilation is deep, steady, and rhythmic. If breathing becomes uncontrolled, ragged, or hyperventilatory within the first 10–15 minutes, the athlete is riding above threshold.
* **Muscular Sensation:** Muscular tension and localized leg fatigue accumulate progressively, but cardiovascular stress remains stable and controlled.

---

## Critical Evaluation of Testing Protocols

```
  Protocol Accuracy vs. Anaerobic Bias
  
  [High Bias / Low Accuracy] ────────────────────────► [Low Bias / High Accuracy]
   Ramp Test (MAP)      2x8-min Test     20-min Test (w/ Blowout)    Long Continuous/TTE Test
```

### 1. Hunter Allen 20-Minute Test (95% Rule)
* **Protocol:** Warm-up $\rightarrow$ **5-minute all-out blowout effort** $\rightarrow$ 10-minute recovery $\rightarrow$ **20-minute maximal time trial** $\rightarrow$ Calculate $FTP = 0.95 \times \text{Average 20-min Power}$.
* **Mechanism:** The 5-minute blowout is specifically designed to deplete anaerobic capacity ($W'$) before starting the 20-minute effort.
* **Limitations:**
  * If the blowout effort is skipped (a very common error), anaerobic capacity significantly inflates the 20-minute power.
  * Even with a blowout, highly trained anaerobic riders regenerate sufficient phosphocreatine and intermediate substrates during the 10-minute rest to still bias the 20-minute result.
  * Pacing errors (going out too hard in the first 5 minutes) frequently cause premature failure.

### 2. Carmichael 2x8-Minute Test (90% Rule)
* **Protocol:** 2 $\times$ 8-minute maximal efforts separated by 10 minutes of easy spinning. Calculate $FTP = 0.90 \times \text{Higher (or Average) 8-min Power}$.
* **Mechanism & Flaws:** 
  * 8 minutes is an intensity heavily dominated by $VO_2max$ and anaerobic energy systems.
  * The 90% multiplier only holds true for ultra-endurance or purely aerobic athletes with virtually no anaerobic power.
  * For athletes with punchy profiles, this test produces massive overestimations (often by 30–50+ Watts).

### 3. Ramp Tests (Step Protocols / MAP Percentage)
* **Protocol:** Continuous incremental ramp (e.g., +15–30 Watts per minute) to voluntary exhaustion. Calculate $FTP = 0.75 \times \text{Maximal Aerobic Power (MAP / peak 1-min power)}$.
* **Mechanism & Flaws:**
  * Ramp tests measure peak aerobic power ($VO_2max$) and anaerobic tolerance, not steady-state lactate clearance.
  * Fractional utilization of $VO_2max$ at threshold varies widely across athletes (from ~65% to 90%). A fixed 75% multiplier is an arbitrary statistical average that misclassifies individual athletes.
  * **Lab vs. Field:** Ramp tests are valuable in laboratory settings when paired with metabolic carts (gas exchange analysis) and continuous blood lactate sampling. As standalone field power tests, they are unreliable for setting threshold training zones.

### 4. Empirical Cycling Progressive / Open-Ended Long Tests
* **Protocol:**
  1. **Phase 1 (Warm-up / Settle-in):** Ride 10–15 minutes at ~10–15 Watts below estimated FTP (target ~90–95%).
  2. **Phase 2 (Target Cadence/Power):** Gradually increase to estimated FTP over 5 minutes and hold steadily.
  3. **Phase 3 (Open-Ended / Ramp to Fatigue):** Once past 30–35 minutes, if feeling strong, increase power by 5–10 Watts every few minutes until exhaustion, or sustain power until cadence drops. Total duration: **35 to 70+ minutes**.
* **Benefits:**
  * Directly measures quasi-steady-state sustainable power while completely eliminating anaerobic distortion.
  * Accurately identifies both **FTP wattage** and current **TTE**.
  * Displays a distinct downward inflection point in the mean-maximal power curve when fatigue occurs.

---

## Practical Application & Prescriptions

### Pacing Rules for Long FTP Tests
1. **Never Start Hard:** The opening 10–15 minutes must feel conservative. Resist the urge to chase high numbers early.
2. **Controlled Ventilation:** Maintain a rhythmic breathing pattern. If hyperventilating in the first half of the test, downshift power immediately.
3. **Listen to the "Burn":** Let the effort come to you. True threshold power feels progressively harder over time due to slow-component kinetics, neuromuscular fatigue, and core temperature rise.

### Prescribing Threshold Training Intervals
* **Do Not Train Above FTP for Threshold Work:** Prescribing intervals at 102–108% of FTP quickly induces excessive autonomic fatigue and relies on anaerobic reserves, cutting total session volume short.
* **Train Sub-Threshold (90–97% FTP):** Prescribing work 10–15 Watts below FTP (high sweet spot / sub-threshold) achieves nearly identical aerobic and mitochondrial adaptations with substantially lower central fatigue:
  * Example progressions: $3 \times 15\text{ min} \rightarrow 2 \times 25\text{ min} \rightarrow 3 \times 20\text{ min} \rightarrow 2 \times 30\text{ min} \rightarrow 1 \times 60\text{ min}$.
* **Ignore Single-Watt Precision:** Training zones represent broad physiological spectra. Chasing single-digit watt precision (e.g., obsessing over 295W vs. 300W) provides zero physiological benefit and increases psychological stress.

---

## Common Pitfalls & Limitations

> [!WARNING]
> **Inflated FTP Cascade:** An overestimated FTP sets all sub-threshold and tempo zones too high. What was intended as an extensive aerobic session turns into an exhaustive glycolytic workout, leading to chronic overreaching and plateaued aerobic development.

1. **"Golden Day" Bias:** Treating an outlier power record achieved under perfect conditions (super-rested, high caffeine, downhill tailwind segment) as everyday operational FTP.
2. **Skipping Depletion Blowouts:** Running a 20-minute test without the preceding 5-minute all-out effort, resulting in an inflated 20-minute average.
3. **Over-Testing / Testing Anxiety:** Subjecting athletes to stressful all-out short tests every 3 weeks. Instead, track threshold progress through regular interval performance (e.g., increasing duration at sub-threshold wattage).

---

## Summary Checklist / Decision Table

### FTP Testing Protocols Comparison

| Protocol | Typical Duration | Anaerobic Bias ($W'$) | Accuracy for True FTP | TTE Identification | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Ramp Test** | 10–15 min | **Extremely High** | Low (uses fixed 75% MAP) | ❌ None | Lab $VO_2max$ / MAP profiling |
| **2 $\times$ 8-min Test** | 2 $\times$ 8 min | **Very High** | Very Low for punchy riders | ❌ None | Time-crunched / pure diesels |
| **20-min Test (No Blowout)** | 20 min | **High** | Poor (overestimates 3–8%) | ❌ None | Not recommended |
| **20-min Test (w/ Blowout)** | 5 min + 20 min | **Moderate** | Moderate (phenotype dependent) | ❌ None | Familiar baseline testing |
| **Long Open-Ended Test** | 35–70+ min | **Negligible** | **Gold Standard** | ✅ Direct measurement | Accurate FTP, TTE, & zone prescription |

### Coach & Athlete Decision Checklist

* [ ] **Identify Rider Phenotype:** Is the athlete an anaerobic/crit specialist or a steady-state diesel? Adjust test selection accordingly.
* [ ] **Choose the Protocol:** Use a continuous progressive long test (35–60 min) for primary threshold baseline determination.
* [ ] **Monitor Ventilation:** Confirm breathing remains rhythmic and steady throughout the first 20 minutes.
* [ ] **Check Pacing:** Ensure the first 10–15 minutes start 10–15 Watts below expected threshold.
* [ ] **Set Training Targets:** Prescribe threshold training intervals 5–15 Watts below tested FTP to accumulate maximum time-in-zone with manageable fatigue.
