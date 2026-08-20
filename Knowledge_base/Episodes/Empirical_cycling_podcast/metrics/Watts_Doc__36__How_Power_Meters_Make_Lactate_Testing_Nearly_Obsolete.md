---
title: "How Power Meters Make Lactate Testing Nearly Obsolete: MLSS, Ramp Flaws, & The Functional Threshold — Complete Guide"
category: "metrics"
topics:
  - "FTP"
  - "LT1_VT1"
  - "LT2_VT2"
  - "Lab_vs_field"
source: "Empirical Cycling Podcast — Kolie Moore & Kyle Hanson (Watts Doc #36)"
author: "Kolie Moore"
date: "2022-03-05"
summary: "A definitive analysis of why direct mechanical power measurement renders laboratory lactate testing largely redundant for cycling training, exploring the history of lactate proxies, the fallacy of fixed 2.0/4.0 mmol thresholds, ramp test kinetics, and the true definition of Functional Threshold Power."
key_takeaways:
  - "Historically, blood lactate testing was developed as an indirect surrogate to estimate human mechanical work capacity; using direct power meter data to attempt to estimate lactate is conceptually backwards."
  - "Fixed blood lactate concentration standards (e.g., 2.0 mmol for LT1, 4.0 mmol for LT2/OBLA) represent population averages that suffer from the fallacy of division; individual MLSS concentrations range widely from 2.5 to >6.5 mmol/L."
  - "Short-stage ramp tests (3- to 5-minute steps) frequently produce severe errors in anaerobic or high-capacity athletes, as early motor unit recruitment floods the blood with lactate before oxidative equilibrium is established."
  - "True physiological threshold is functionally defined as the inflection point on the power-duration curve above which fatigue accelerates exponentially and below which fatigue accumulates slowly."
  - "Power meters allow continuous, non-invasive, day-to-day evaluation of the power-duration relationship (TTE, W', and FTP) under real-world conditions, outperforming periodic invasive lab pinpricks."
---

# How Power Meters Make Lactate Testing Nearly Obsolete: MLSS, Ramp Flaws, & The Functional Threshold — Complete Guide
_Source: Empirical Cycling Podcast — Kolie Moore & Kyle Hanson (Watts Doc #36)_

---

## What Is the Core Inversion of Lactate Testing?

For nearly a century, exercise physiologists sought a safe, submaximal, and reproducible method to determine human endurance capacity without forcing subjects to catastrophic exhaustion in maximal $\text{VO}_2\text{max}$ tests. Blood lactate concentration was adopted as an **indirect metabolic proxy for mechanical power output**.

```
                   The Historical Inversion of Lactate Testing
                   
   Historical Scientific Paradigm (1930–1990):
   [ Unknown Human Work Capacity ] ◄── Measured via ── [ Blood Lactate Concentration (Proxy) ]
   
   The Modern Power Meter Reality (2000–Present):
   [ Direct Mechanical Power (Watts) ] ──► Accurately and directly measures work capacity!
   
   The Absurd Modern Loop:
   [ Direct Power Meter (Watts) ] ──► Used to pace ──► [ Lactate Pinprick ] ──► To estimate [ Power! ]
```

With modern direct force power meters, athletes possess the exact variable (mechanical wattage over time) that laboratory lactate testing was originally invented to estimate.

---

## Key Physiological Mechanisms / How to Think About It

### 1. The Fallacy of Fixed Lactate Concentrations (4.0 mmol Myth)

The widespread adoption of **$2.0\text{ mmol/L}$ (LT1)** and **$4.0\text{ mmol/L}$ (LT2 / OBLA)** stems from early population studies (Mader & Heck, 1986; Stegmann, 1982). 

While the population mean at Maximal Lactate Steady State (MLSS) frequently averages $\sim 4.0\text{ mmol/L}$, applying this average to an individual athlete commits the **fallacy of division**:

```
 Individual vs. Population MLSS Lactate Concentrations (Mader & Heck Data):
 ┌──────────────────────┬────────────────────────────┬────────────────────────────┐
 │ Subject Pool         │ MLSS Concentration Range   │ Mean ± SD                  │
 ├──────────────────────┼────────────────────────────┼────────────────────────────┤
 │ 16 Trained Subjects  │ 3.0 to 5.5 mmol/L          │ 4.02 ± 0.70 mmol/L         │
 │ Untrained / Sprint   │ 4.5 to 6.6+ mmol/L         │ Variable                   │
 │ Elite Diesel / Ultra │ 2.0 to 3.2 mmol/L          │ Variable                   │
 └──────────────────────┴────────────────────────────┴────────────────────────────┘
```

* An athlete with a true MLSS at $2.8\text{ mmol/L}$ trained at a fixed $4.0\text{ mmol/L}$ target will be chronically over-training above threshold.
* An athlete with a true MLSS at $5.5\text{ mmol/L}$ trained at a fixed $4.0\text{ mmol/L}$ target will be training significantly below threshold.

---

### 2. Ramp Test Flaws: Why Short Stages Fail High-Capacity Riders

Standard commercial lactate protocols use graded exercise tests with $3\text{--}5\text{ minute}$ stages. In athletes with large anaerobic capacity ($W'$) or high fast-twitch motor unit recruitment, short stages fail catastrophically:

```
                   The World Champion Case Study (3-Min Ramp)
                   
   Stage Power (Watts)    Blood Lactate (mmol/L)    Standard Interpretation
   ─────────────────────────────────────────────────────────────────────────
    0 W                   1.6 mmol/L
   150 W                  1.7 mmol/L
   250 W                  1.9 mmol/L                ◄── Classic "LT1" (~240W)
   275 W                  3.1 mmol/L
   300 W                  5.3 mmol/L                ◄── Classic "LT2 / 4 mmol" (~285W)
   325 W                  8.3 mmol/L
   350 W                  9.8 mmol/L
   375 W                 12.6 mmol/L
   400 W                 16.0 mmol/L                (Test Terminated)
   ─────────────────────────────────────────────────────────────────────────
   Laboratory Prediction:   FTP = 280–290 Watts
   Actual Field FTP:        FTP = 370 Watts (Holds for >45–50 minutes!)
```

#### Why Did Lactate Skyrocket at 300 W?
1. **Lagging Oxidative Kinetics:** At the onset of a new step, sympathetic drive and sudden cross-bridge turnover trigger rapid glycolysis.
2. **Efflux Dynamics:** Newly recruited fibers efflux massive quantities of lactate ($>9,000\text{ }\mu\text{mol}\cdot\text{L}^{-1}\cdot\text{min}^{-1}$) into the bloodstream.
3. **Equilibrium Time:** It requires $8\text{--}15\text{ minutes}$ for muscle blood flow, mitochondrial uptake, and systemic clearance to reach equilibrium. In a 3-minute stage, the tester measures transient peak efflux, not steady-state balance.

---

### 3. Untrained Kinetics: Violating the 1.0 mmol MLSS Rule

The clinical definition of MLSS requires blood lactate to rise by **$\le 1.0\text{ mmol/L}$ between minute 10 and minute 30** of a constant-load test.

* In an untrained endurance individual with high muscle mass (e.g., Kolie Moore at $190\text{ W}$ threshold):
  * Minute 10: $4.9\text{ mmol/L}$
  * Minute 20: $5.7\text{ mmol/L}$
  * Minute 30: $6.6\text{ mmol/L}$ ($\Delta = +1.7\text{ mmol/L}$)
* Despite failing the clinical $<1.0\text{ mmol/L}$ criterion, $190\text{ W}$ represented the athlete's true sustainable functional threshold. Low peripheral mitochondrial density in recruited motor units causes continuous minor lactate accumulation throughout steady-state work without representing exponential catastrophic failure.

---

## Practical Application & Prescriptions

### 1. Functional Definition of Threshold

Forget blood concentrations; physiological threshold is defined purely by **performance sustainability**:

> **Kolie Moore's Definition of Threshold:**  
> *"The work rate above which someone fatigues exponentially faster, and below which someone fatigues significantly slower."*

```
                     The Power-Duration Log-Curve Inflection
                     
   Power (W)
     │
 600 │  ● (Sprint / W' Domain)
     │   \
 400 │    \
     │     \
 350 │      └───●───────────────────────────● (Threshold / FTP Plateau)
     │           \                           \
 300 │            \                           \── (Aerobic Base / Z2)
     │             \                           \
     └──────────────┴───────────────────────────┴──────────► Log Time
                  1 min                       45-70 min (TTE)
```

### 2. Pacing LT1 and LT2 in the Real World

```
 Practical Field Methods for Threshold Determination:
 ┌──────────────────────┬────────────────────────────┬────────────────────────────┐
 │ Threshold Level      │ Primary Field Marker       │ Verification Protocol      │
 ├──────────────────────┼────────────────────────────┼────────────────────────────┤
 │ LT1 (Aerobic Base)   │ "Hardest riding that still │ Talk test / Nasal breathing│
 │                      │  feels distinctly easy"    │ HR drift <5% over 2.5–3h   │
 ├──────────────────────┼────────────────────────────┼────────────────────────────┤
 │ LT2 (FTP / MLSS)     │ Power-duration inflection; │ 35–60 min TTE Test         │
 │                      │ RPE 7–8/10, stable cadence │ (Empirical Testing Prot.)  │
 └──────────────────────┴────────────────────────────┴────────────────────────────┘
```

---

## Common Pitfalls & Limitations

1. **Blindly Trusting Automated Ramp-Test Software:** Commercial software drawing polynomial curves through 3-minute steps often misidentifies threshold by $40\text{--}80\text{ W}$.
2. **Assuming Critical Power (CP) Equals MLSS:** 2-parameter mathematical CP models using short tests ($2\text{--}12\text{ min}$) systematically overestimate sustainable threshold power by $15\text{--}30\text{ W}$.
3. **Ignoring Hydration and Skin Contamination:** Sweat contains lactate; failing to properly wipe skin with alcohol before pricking or testing during severe dehydration distorts blood concentration readings by $>1.0\text{--}2.0\text{ mmol/L}$.

---

## Summary Checklist / Decision Table

| Metric / Tool | Laboratory Lactate Testing | Power Meter & Field Testing | Coaching Recommendation |
| :--- | :--- | :--- | :--- |
| **Measurement Type** | Invasive, episodic blood pinprick | Non-invasive, continuous second-by-second | Rely on power meters for day-to-day training and testing. |
| **Accuracy on Individual** | Compromised by fixed population criteria | Direct measurement of mechanical output ($n=1$) | Determine individual power-duration curve inflection. |
| **Stage Duration Bias** | 3-minute steps overestimate fatigue in anaerobic types | Long duration tests ($35\text{--}60\text{ min}$) eliminate warmup bias | Use progressive threshold tests ($1\times 40\text{--}60\text{ min}$). |
| **Cost & Accessibility** | High (\$150–\$300 per lab test) | One-time equipment purchase | Invest in a quality on-bike power meter over lab tests. |
| **Actionability** | Yields historical snapshot under artificial conditions | Yields real-time feedback in race/training environments | Guide intervals by power, RPE, and heart rate integration. |
