---
title: Ftp Vs Cp
category: physiology
topics:
- FTP
- CP
- W_prime
source: Knowledge Base
author: Endurance Research
date: '2025-01-01'
summary: 'title: FTP vs. Critical Power — Complete Guide category: metrics'
---

  |'
---

# FTP vs. Critical Power — Complete Guide

_Source: Empirical Cycling Podcast — Kolie Moore & Kyle_

---

## What Each Model Measures

| Model             | What it is                                                                      |
| ----------------- | ------------------------------------------------------------------------------- |
| **FTP**           | Power at maximal lactate steady state — the highest sustainable aerobic output  |
| **Critical Power** | A fitting parameter from a mathematical model — the slope of a work-time line  |

Both attempt to find the power above which fatigue accelerates rapidly. They are not the same thing and are **not interchangeable**, though for some athletes the numbers converge.

---

## How Critical Power Is Derived

CP is a **linear model** fitted to 2–5 max-effort data points between ~30 sec and 20 min:

1. Plot **total kilojoules burned** (y-axis) vs. **duration in seconds** (x-axis)
2. Fit a straight line — the **slope** is Critical Power, the **intercept** is W' (anaerobic capacity)
3. That straight line is mathematically equivalent to the hyperbolic power-duration curve

**Why it looks accurate short-term:** within its fitted range (roughly 1–20 min), the linear model is a reasonable approximation of the human power curve. Outside that range, it breaks down.

**The fundamental flaw:** the model predicts you can sustain CP for an **infinite duration**. In physics, any model that produces infinity is outside its valid domain. CP is a valid interpolation tool — it is **not** a valid extrapolation tool.

---

## FTP vs. CP: How Different Are They?

They are **similar for many athletes, significantly different for others** — especially anaerobic athletes.

**Key study** (_Maximal lactate steady state, respiratory compensation threshold, and critical power_):
- Trained subjects, robust methodology
- CP average: **278 W**
- MLSS (FTP) average: **239 W**
- **Difference: ~39 W** — statistically significant on average

Other studies find no significant difference, but many use small samples or methodologies that obscure individual variation.

**Practical example (anaerobic athlete):**
- CP from model: 304 W
- Actual FTP: ~285–290 W
- Difference: ~15–20 W (~7%)
- At sweet spot or threshold, that 7% gap makes intervals very hard or impossible

> If CP and FTP are within ~2 W: effectively identical. If the gap is 15–40 W: using CP as FTP will cause systematic over-prescription.

---

## Where Each Model Is Valid

| Intensity Zone          | Better model to use         | Reason                                                           |
| ----------------------- | --------------------------- | ---------------------------------------------------------------- |
| Above FTP / VO2max zone | Critical Power              | CP fits well within its 1–20 min fitted range                   |
| At and below FTP        | FTP                         | CP overestimates sustainable power; FTP reflects actual MLSS    |
| Zone 2 / long endurance | Neither extrapolation       | CP extrapolated to 1–2+ hr durations produces absurd predictions |

A practical rule: **interpolate with CP, never extrapolate. Use FTP to prescribe training below threshold.**

---

## Why CP Appears in Training Software

CP is easy to compute (fit a line to 2–5 points, extractable from any ride history) and was built into Golden Cheetah early on. This caused it to occupy the same UI space as FTP — not because they are equivalent, but because CP is trivial to implement. FTP requires deliberate testing or physiological modeling and cannot be automatically extracted from ride data without context.

---

## Pros and Cons

### FTP

**Pros**
- Reflects an actual physiological state (MLSS)
- Reliable for prescribing intervals at and below threshold
- Updates with training; usable as a living model
- Better at predicting what an athlete can sustain over 30–90 min

**Cons**
- Requires deliberate testing (time-consuming)
- Does not describe what happens above FTP — that is individual and needs separate assessment
- The "95% × 20-min power" shortcut has high individual error

### Critical Power

**Pros**
- Common in scientific literature (easy to compute in lab settings)
- Valid and useful within its fitted duration range (1–20 min approx.)
- Useful for modeling anaerobic capacity (W') and short efforts
- Can be derived from existing ride data without a dedicated test

**Cons**
- Assumes infinite sustainable duration at CP — physiologically false
- Overestimates FTP for many athletes, especially anaerobic riders
- Fitting only peaks on the power curve (as Golden Cheetah does by default) inflates the result further
- Was designed as a **laboratory physiological model**, not a field training tool

---

## The "Gray Zone" Between FTP and CP

Research shows a gray zone between FTP (MLSS) and CP where:
- You will exhaust yourself before reaching VO2max
- Fatigue is faster than below FTP but without the VO2max stimulus
- This zone shifts with fatigue, glycogen status, and training state — it is not a fixed boundary

Training in this zone is neither efficient threshold work nor effective VO2max work. It's particularly relevant when CP is used as FTP and intervals are inadvertently prescribed in this zone.

---

## Decision Guide: Which to Use

| Purpose                          | Use         | Why                                                    |
| -------------------------------- | ----------- | ------------------------------------------------------ |
| Setting threshold intervals      | FTP         | CP may significantly overestimate sustainable power    |
| Modeling 3–10 min efforts        | CP          | Within its valid range                                 |
| Estimating anaerobic capacity    | CP (W')     | W' is a CP model output                                |
| Pacing a long time trial         | FTP         | CP extrapolated to 30–60 min is unreliable             |
| Analyzing short power curve data | Either      | Both converge in the 5–20 min zone for most riders     |
| Prescribing sweet spot / tempo   | FTP         | CP inflation creates systematically too-hard intervals |

---

## Key Takeaway

FTP and CP are **different tools with different valid domains** — not two measurements of the same thing. Using CP where FTP belongs, or vice versa, doesn't mean one model is wrong; it means the model is being applied outside its design intent. Knowing how each model is constructed and where it breaks down is the prerequisite for using either correctly.
