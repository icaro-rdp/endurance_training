---
title: 'FTP vs. Critical Power: Models vs. Physiology — Complete Guide'
category: training
topics:
- Threshold_intervals
- VO2max_and_aerobic_hiit
- FTP_and_functional_metrics
- Critical_power_and_w_prime
- Pacing_and_execution_dynamics
source: 'Empirical Cycling Podcast — Kolie Moore & Kyle Hanson (Watts Doc #8)'
author: Kolie Moore
date: '2019-06-04'
summary: The document discusses the differences between Functional Threshold Power
  (FTP) and Critical Power (CP), their mathematical and physiological origins, and
  their practical applications in training and performance. It emphasizes the importance
  of using FTP for aerobic threshold training and CP for severe-domain pacing, while
  highlighting the limitations of CP as a proxy for FTP.
key_takeaways:
- FTP is a physiological metric representing power at Maximal Lactate Steady State
  (MLSS), whereas Critical Power (CP) is a mathematical parameter derived from curve-fitting.
- The 2-parameter CP model (Work = W' + CP * t) mathematically assumes CP can be held
  for infinite duration, violating human biological fatigue constraints.
- In athletic populations—especially punchy riders with large anaerobic capacity (W')—CP
  frequently overestimates true FTP/MLSS by 15 to 40 Watts.
- CP is highly valid for interpolating performance between 2 and 20 minutes, but invalid
  for extrapolating extended endurance or setting sustainable sub-threshold training
  zones.
- Prescribing threshold intervals (e.g., 3x20 min) using an unadjusted mathematical
  CP number leads to premature task failure and excessive autonomic fatigue.
---
# FTP vs. Critical Power: Models vs. Physiology — Complete Guide
_Source: Empirical Cycling Podcast — Kolie Moore & Kyle Hanson (Watts Doc #8)_

---

## What Are FTP and Critical Power?

Functional Threshold Power (FTP) and Critical Power (CP) are frequently used interchangeably in cycling software (such as GoldenCheetah or open-source power analyzers) and endurance literature to denote the boundary between sustainable aerobic exercise and rapid fatigue. However, they are fundamentally distinct in origin, mathematical formulation, and physiological meaning:

* **Functional Threshold Power (FTP):** Conceived by Dr. Andrew Coggan as a field proxy for **Maximal Lactate Steady State (MLSS)**. It represents the highest quasi-steady-state power output where blood lactate and metabolic homeostasis remain stable. It is tied to an athlete's individual Time-to-Exhaustion (TTE, typically 35–80+ minutes).
* **Critical Power (CP):** Conceived by Monod and Scherrer (1965), CP is a **mathematical asymptote** derived from linear or hyperbolic modeling of maximal power tests. It represents the theoretical boundary separating the heavy exercise domain from the severe exercise domain.

---

## Key Physiological Mechanisms / How to Think About It

```
                  The Two-Parameter Critical Power Model
  
    Hyperbolic Power-Duration Curve              Linear Work-Time Relationship
  Power (W)                                   Work (kJ)
   ▲                                            ▲
   │  ╲                                         │             / (Slope = CP)
   │   ╲                                        │           /
   │    ╲                                       │         /
   │     ─────── Asymptote (CP)                 │       /
   │                                            │  W' ┌/ (Y-intercept = W')
   └─────────────────────────► Time             └─────┴────────────────────► Time (s)
     P(t) = CP + (W' / t)                         Work(t) = W' + (CP · t)
```

### 1. The Mathematics of Critical Power
The classic two-parameter CP model relies on the linear relationship between total work performed ($W_{\text{total}}$ in kilojoules) and time ($t$ in seconds):
$$W_{\text{total}} = W' + (\text{CP} \times t)$$
$$\text{Power}(t) = \text{CP} + \frac{W'}{t}$$

* **$\text{CP}$ (Slope):** The critical power output in Watts.
* **$W'$ (Y-Intercept):** The finite work capacity available above CP (measured in kilojoules), derived from anaerobic phosphocreatine and fast glycolytic reserves.
* **The "Infinite Duration" Mathematical Flaw:** Because CP is the mathematical asymptote of a hyperbola, the pure equation predicts that an athlete can produce CP for infinite time without exhausting. In physical reality, glycogen depletion, core temperature rise, neuromuscular transmission failure, and cardiorespiratory strain cause power to decay steadily below CP beyond 30–60 minutes.

### 2. Why CP Systematically Overestimates True FTP / MLSS
When CP is calculated using short laboratory or field bouts (e.g., 1-min, 3-min, and 10-min tests, or 3-min and 20-min tests), two major confounders occur:
1. **Mathematical Leverage of Anaerobic Capacity ($W'$):** Athletes with punchy neuromuscular profiles or large sprint capacities produce immense energy from anaerobic glycolysis during 1-to-5-minute efforts. This inflates the slope of the linear fit, rotating the CP line upward.
2. **Scientific Discrepancies:** Multiple rigorous studies (e.g., Mattioni Maturana et al.) have demonstrated that CP is systematically higher than MLSS:
   * In trained cyclist cohorts, mean **CP is often 15 to 40 Watts higher than true MLSS/FTP** (e.g., a study finding mean CP of 278W vs. MLSS of 239W — a 39-Watt disparity).
   * While some small-sample lab studies declare them "statistically not significantly different" due to wide confidence intervals, a 15–20 Watt discrepancy in the field is the difference between completing a $3 \times 20\text{-minute}$ workout and blowing up on rep 1.

```
 Exercise Intensity Domains & The CP / MLSS Disconnect
 ┌─────────────────────────────────────────────────────────────┐
 │ Extreme Domain   (Task failure in <2 min; Neuromuscular)   │
 ├─────────────────────────────────────────────────────────────┤
 │ Severe Domain    (VO2 kinetics drift to VO2max; W' depletes)│
 │                                                             │ ◄── Critical Power (CP)
 ├─────────────────────────────────────────────────────────────┤
 │ Heavy Domain     (Elevated but stable lactate; quasi-steady)│
 │                                                             │ ◄── FTP / MLSS
 ├─────────────────────────────────────────────────────────────┤
 │ Moderate Domain  (Below LT1/VT1; Pure oxidative steady-state│
 └─────────────────────────────────────────────────────────────┘
```

### 3. Interpolation vs. Extrapolation
* **Interpolation (Valid):** The CP model is exceptional at predicting performance *within* the domain of its test points (e.g., calculating expected pacing for a 4-minute pursuit or an 8-minute hill climb).
* **Extrapolation (Invalid):** Using a model fitted on 3-minute and 12-minute tests to predict sustainable power at 45, 60, or 120 minutes is mathematically and physiologically invalid.

---

## Practical Application & Prescriptions

### 1. When to Use FTP vs. Critical Power

```
 Metric Selection Decision Flowchart
 ┌───────────────────────────────────────────────────────────────┐
 │ What is the primary training or performance objective?        │
 └───────────────┬───────────────────────────────┬───────────────┘
                 │                               │
                 ▼                               ▼
     [ Threshold & Sub-Threshold ]       [ Severe Domain & Pacing ]
     • Prescribing Sweet Spot / FTP      • Modeling 2–8 min hill climbs
     • Managing aerobic base & TTE       • Track pursuit / Crit surges
     • Long race durability (>40 min)    • Estimating W' expenditure
                 │                               │
                 ▼                               ▼
           Use TRUE FTP                    Use CP & W'
     (MLSS / Long Open-Ended Test)     (Multi-point power duration)
```

### 2. Prescribing Threshold Intervals: Avoid the "CP Ego Trap"
* **The Pitfall:** An athlete with an actual FTP of 280W (TTE 45 min) gets a modeled CP of 305W from GoldenCheetah. They attempt $3 \times 20\text{ min}$ at 305W. Because 305W is in the severe domain, they deplete $W'$ within 14 minutes, experience acute acidosis, and fail the session.
* **The Solution:** Always calibrate threshold intervals using direct sustained field tests (e.g., Empirical Cycling long progressive test) or set workouts at 92–95% of estimated threshold to ensure steady-state aerobic flux.

### 3. Utilizing $W'$ in Race Analysis
While CP should not be used directly for long threshold targets, the **$W'$ (Anaerobic Work Capacity)** parameter is highly valuable:
* Tracking $W'$ balance ($W'_{\text{bal}}$) in race files reveals how deeply an athlete depleted their anaerobic battery during repetitive criterium or short climb surges.
* Useful for diagnosing whether a rider got dropped due to aerobic ceiling limitations or $W'$ exhaustion.

---

## Common Pitfalls & Limitations

> [!WARNING]
> **The Software Auto-CP Hazard:** Many training platforms automatically calculate CP using standard 2-point algorithms (e.g., 3-minute and 20-minute bests). If the 20-minute best was performed as an aggressive, punchy climb with high anaerobic involvement, the resulting CP will be massively inflated, rendering subsequent workout targets unusable.

1. **Equating Mathematical Asymptote with Infinite Endurance:** Believing an athlete can sustain CP indefinitely. Historical misapplications (such as modeling Roman military marches at CP for 7 hours) highlight the absurdity of unconstrained mathematical extrapolation.
2. **Ignoring Time-to-Exhaustion (TTE):** Assuming all athletes at CP or FTP have identical endurance capacity. TTE varies dynamically from 35 to 80+ minutes based on aerobic volume.
3. **Prescriptive Over-Reliance:** Treating any power model as an absolute predictor of race day wattage rather than allowing the athlete to pace dynamically by physiological sensation, ventilatory control, and real-time feedback.

---

## Summary Checklist / Decision Table

### FTP vs. Critical Power Comparison

| Parameter | Functional Threshold Power (FTP) | Critical Power (CP) |
| :--- | :--- | :--- |
| **Origin / Nature** | Physiological / Field Proxy (MLSS) | Mathematical / Curve Fitting |
| **Foundational Formula** | Quasi-steady-state metabolic flux | $W_{\text{total}} = W' + (\text{CP} \times t)$ |
| **Domain Boundary** | Heavy-to-Severe metabolic boundary | Severe domain mathematical asymptote |
| **Typical Value** | Accurately matches MLSS | Systematically higher by 10–40W in punchy riders |
| **Duration Constraint** | Finite (TTE: 35–80+ min) | Mathematically infinite ($\infty$) |
| **Primary Utility** | Prescribing Zone 2, Sweet Spot, & FTP | Pacing 2–10 min efforts; calculating $W'$ battery |
| **Testing Requirement** | Long open-ended test (35–60 min) | 2 to 4 maximal efforts (e.g., 1, 3, 7, 12 min) |

### Coach & Athlete Implementation Checklist

* [ ] **Determine the Purpose:** Use FTP for aerobic threshold zone prescription; use CP and $W'$ for severe-domain modeling and short-duration pacing.
* [ ] **Cross-Check Software CP:** If GoldenCheetah or third-party software outputs a CP significantly higher than 40-minute power, do not use it for threshold intervals.
* [ ] **Test Sufficient Durations:** When generating a multi-point CP curve, include at least one effort $\ge 12–20$ minutes to provide mathematical leverage against short-duration sprint bias.
* [ ] **Validate in the Field:** Ensure athletes can sustain their prescribed threshold power with rhythmic ventilation and steady RPE for $\ge 30–40$ continuous minutes.
