---
title: "Quantifying Diminishing Returns: Longitudinal Growth Modeling, Asymptotes, and Season Planning — Complete Guide"
category: "periodization"
topics:
  - "Volume_quantification"
  - "Block_periodization"
  - "Aerobic_base"
source: "Empirical Cycling Podcast — Kolie Moore & Kyle Hanson (Watts Doc #61)"
author: "Kolie Moore"
date: "2026-02-05"
summary: "An analytical deep dive into training diminishing returns using large-scale longitudinal growth modeling (n=14,690 over 6.8 years), multi-year cycling FTP tracking, and mathematical frameworks for managing athlete expectations and season planning."
key_takeaways:
  - "Long-term athletic adaptation follows a logarithmic growth curve rather than a linear trajectory; log-transforming time renders the adaptation rate linear for quantitative modeling."
  - "The 'change point' (the inflection point where rapid adaptation transitions to slow diminishing returns) occurs around weeks 26–31 on average, with significant right-skewed individual variation."
  - "Short-term training studies (4–8 weeks) evaluate athletes on the steep initial limb of the growth curve, frequently mistaking a faster rate of early ascent for a higher long-term ceiling (asymptote)."
  - "In multi-year cycling development, annual FTP gains naturally compress (e.g., +45W Year 1 → +25W Year 2 → +15W Year 4 → +10W Year 5); late-stage 10W gains represent outstanding progress."
  - "True genetic limits are a diagnosis of exclusion; most amateur plateaus stem from unaddressed physiological bottlenecks (e.g., VO2max ceiling) or recovery constraints rather than fixed biological ceilings."
---

# Quantifying Diminishing Returns: Longitudinal Growth Modeling, Asymptotes, and Season Planning — Complete Guide
_Source: Empirical Cycling Podcast — Kolie Moore & Kyle Hanson (Watts Doc #61)_

---

## What Are Diminishing Returns in Athletic Training?

Diminishing returns describes the fundamental biological phenomenon wherein each successive unit of training stimulus yields a progressively smaller increment of physiological adaptation and performance gain. While athletes and coaches intuitively acknowledge that progress slows over time, training literature often models adaptations linearly or focuses on short-term interventions that fail to capture multi-year adaptation curves.

```
Longitudinal Adaptation Trajectory:
 Performance / Watts
      ▲
      │                 ┌───────────────────────► High-Level Asymptote / Ceiling
      │            .---'  (Years 3–7: +5 to +10W/year; High Fatigue Cost)
      │        .--'
      │      .'  ◄── Change Point / Knee (Weeks 26–31)
      │    .'
      │   /  (Months 1–6: Rapid "Newbie" Adaptation; +30 to +50W/year)
      │  /
      └─┴────────────────────────────────────────► Training Time (Weeks / Years)
```

By applying **retrospective longitudinal growth modeling** to massive training datasets, coaches can mathematically quantify adaptation rates, identify inflection points ("change points"), and accurately structure multi-year periodization.

---

## Key Physiological Mechanisms & Mathematical Modeling

### 1. The Steele et al. Benchmark Dataset ($n = 14,690$)

To establish the mathematical architecture of long-term human adaptation, Steele et al. analyzed 14,690 participants over up to **352 weeks (6.8 years)** performing standardized, supervised resistance exercise (1 set of 4–6 repetitions to momentary muscular failure, standardized 8–10s eccentric/concentric cadences, 1 session per week):

* **Growth Modeling:** Raw adaptation curves follow a logarithmic or power function:
  $$y(t) = a + b \cdot \ln(t)$$
  * $y(t)$: Strength or power output at time $t$
  * $a$: Baseline starting value
  * $b$: Adaptation rate parameter
* **Log Transformation:** When the time axis is log-transformed ($\ln(\text{weeks})$), the adaptation trajectory becomes strictly linear ($R^2 > 0.95$), confirming a power-law relationship in human neuromuscular and metabolic adaptations.
* **The First Derivative & Change Point Distribution:**
  Taking the first derivative ($d/dx$) of the logarithmic curve produces a hyperbolic rate of change ($1/t$). The "change point" (the knee where rapid adaptation slows) exhibited a **strongly right-skewed distribution**:
  * **Mode (Peak Density):** Occurred between **weeks 26 and 31** across major compound movements.
  * **Tails:** Some low-responders plateaued within 8–12 weeks, while high-responders continued steady upward trajectories beyond 250 weeks (~5 years).

```
Distribution of Individual Change Points (Weeks to Plateau Transition):
 Frequency
    ▲
    │   ████
    │  ██████
    │  ████████ ◄── Mode: Weeks 26–31
    │  ██████████
    │  ████████████
    │  ████████████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒► (Tail out to 250+ weeks)
    └──┴──────────────────────────────────────────► Time (Weeks)
```

* **Effect Size Compression:**
  * **Weeks 1–12:** Large effect sizes ($d = 0.58\text{–}0.86$).
  * **By Week 6:** Weekly effect size drops to $\approx 0.07$.
  * **Cumulative Shift:** Year 1 accounted for **30–50% improvement**, while Years 2 through 6 yielded only an additional **10–20% combined**.
  * **No Survivorship Bias:** Refitting models exclusively on dropouts vs. multi-year completers showed identical early-stage adaptation slopes.

---

### 2. Diminishing Returns in Cycling (Multi-Year Power Progression)

Long-term cycling Functional Threshold Power (FTP) data demonstrates identical power-law dynamics across competitive athletes:

```
Case Study: 5-Year Multi-Year FTP Progression (Clean Longitudinal Data)
┌──────────┬─────────────┬────────────────┬───────────────────────────┐
│ Timeline │ FTP (Watts) │ Absolute Gain  │ Annual Rate of Change     │
├──────────┼─────────────┼────────────────┼───────────────────────────┤
│ Baseline │ 280 W       │ —              │ —                         │
│ Year 1   │ 325 W       │ +45 W          │ +16.1% (Rapid Base Phase) │
│ Year 2   │ 350 W       │ +25 W          │ +7.7%                     │
│ Year 3   │ 375 W       │ +25 W          │ +7.1%                     │
│ Year 4   │ 390 W       │ +15 W          │ +4.0%                     │
│ Year 5   │ 400 W       │ +10 W          │ +2.6% (Late Asymptote)    │
└──────────┴─────────────┴────────────────┴───────────────────────────┘
Total 5-Year Gain: +120 Watts (+42.8% above baseline) | Best Fit: Power Series Growth Model (R² = 0.98)
```

#### Intra-Season Layoffs and Retracing the Growth Curve
When an athlete takes a 2–4 week end-of-season layoff, fitness drops to an intermediate baseline (e.g., falling from 375W to 320W). Upon resuming training:
* **Quarter 1 (Months 1–3):** Rapid re-adaptation (+30W to 350W), quickly retracing previous gains.
* **Quarter 2 (Months 4–6):** Slower ascent (+12W to 362W).
* **Quarter 3 (Months 7–9):** Peak consolidation (+13W to 375W).
* **Quarter 4 (In-Season):** Maintenance and racing performance at the plateau.

```
       Intra-Season Retracing Dynamics:
 FTP (W)
  380 ┼─────────────────────────────────● (Q3/Q4: 375W Plateau)
  360 ┼───────────────────────● (Q2: 362W)
  340 ┼─────────────● (Q1: 350W)
  320 ┼─● (Post-Offseason Baseline: 320W)
      └─┴───────────┴─────────┴─────────┴────────► Time (Quarters)
```

---

## The Scientific Literature Interpretation Fallacy

Most sports science training studies suffer from structural design limitations that lead to flawed coaching takeaways:

> [!WARNING]
> **The Rate of Ascent vs. Ceiling Fallacy:** A 6-week study showing Protocol A (e.g., Sprint Interval Training) produces 2x the $\text{VO}_2\text{max}$ gain of Protocol B (e.g., Steady Threshold) does **not** mean Protocol A produces a higher long-term ceiling. It merely proves that Protocol A accelerates the athlete up the steep initial limb of the growth curve faster.

```
Short-Term Study Horizon vs. Long-Term Adaptation Asymptote:
 Watts
   ▲
   │        / Protocol A (HIIT/SIT: Rapid Early Ascent) ──► Flatlines early
   │       /
   │      /      / Protocol B (Base/Extensive: Slower Ascent) ──► Higher Ceiling
   │     /      /
   │    /      /
   │   /      /
   │  ┌──────┐
   │  │Study │ (4–8 Weeks Window: Protocol A looks massively superior)
   │  └──────┘
   └──┴──────────────────────────────────────────────────────► Time
```

1. **Short Study Durations (4–8 Weeks):** Almost universally capture the transient non-specific adaptation phase occurring on the left side of the change point.
2. **Subject Selection Bias:** Untrained or off-season athletes respond non-specifically to *any* novel stimulus; Sprint Interval Training, Sweet Spot, and Zone 2 all raise $\text{VO}_2\text{max}$ and threshold simultaneously in this population.
3. **Multi-Focal Adaptations in Cycling:** Unlike resistance training (where force and cross-sectional area dominate), endurance performance depends on distinct, semi-independent systems:
   * **Central:** Left ventricular volume, stroke volume, systemic blood volume.
   * **Peripheral:** Capillary density, mitochondrial enzyme concentration, MCT1/MCT4 transport, muscle fiber type shifts.
   * Treating endurance as a single growth curve obscures the fact that different subsystems hit plateaus at different times.

---

## Practical Application & Prescriptions

### 1. Diagnosing Bottlenecks When Progress Flatlines

When an athlete encounters a plateau on their current growth curve, continuing to hammer the same stimulus produces fatigue without adaptation. Identify and target the specific physiological limiter:

```
                  Athlete Plateau at Threshold (FTP)
                                  │
      ┌───────────────────────────┴───────────────────────────┐
      ▼                                                       ▼
[Case 1: Fractional Ceiling Hit]           [Case 2: Base / Durability Deficit]
 FTP is 85–88% of VO2max.                   TTE at FTP is short (<35–40 min) or
 Muscular endurance is high, but            power degrades rapidly after 2,000 kJ.
 stroke volume/VO2max limits ceiling.       Aerobic base and capillarization lagging.
      │                                                       │
      ▼                                                       ▼
[Prescription: VO2max Block]               [Prescription: Extensive Base & TTE]
 3–4 weeks of high-intensity aerobic        Extend interval duration at 90–95% FTP
 intervals (e.g., 4x5 min all-out)         (e.g., 3x20 → 2x30 → 1x60 min) plus
 to lift the central ceiling.              high-volume Zone 2 volume.
```

### 2. Managing Multi-Year Season Expectations

Coaches and self-coached athletes must align goals with their chronological position on the adaptation curve:

| Athlete Phase | Training Age | Expected Annual FTP Gain | Target Primary Adaptation | Periodization Focus |
| :--- | :--- | :--- | :--- | :--- |
| **Novice / Development** | 0–2 years | $+30\text{ to }+50\text{ Watts}$ | Base mitochondrial density, general aerobic capacity | Consistent volume, basic sub-threshold progressions |
| **Intermediate** | 3–4 years | $+15\text{ to }+25\text{ Watts}$ | Fractional utilization, specific $\text{VO}_2\text{max}$ expansion | Polarized/Pyramidal blocks, TTE extension (45–70 min) |
| **Advanced / Elite** | 5+ years | $+5\text{ to }+15\text{ Watts}$ | Durability ($>40\text{ kJ/kg}$), high-intensity repeatability | Concentrated $\text{VO}_2\text{max}$ micro-blocks, distributed race-specific intervals |

---

## Common Pitfalls & Limitations

1. **The "Comparison Is the Thief of Joy" Trap:** Comparing one's Year 4 gains (+10W) to a teammate's Year 1 gains (+40W). Progress must be evaluated against one's own historical growth model.
2. **Prematurely Claiming a Genetic Ceiling:** Declaring oneself "genetically limited" when progress stalls, rather than addressing unmanaged life stress, sleep deficits, inadequate fueling, or stale interval architecture. True genetic limits are an extreme diagnosis of exclusion.
3. **Endless Threshold Grinding:** Repeating the exact same $2 \times 20\text{ min}$ threshold session year-round. Once threshold fractional utilization plateaus near $\sim 85\%$ of $\text{VO}_2\text{max}$, further threshold training yield drops to near zero.
4. **Panic Over Mid-Season Layoffs:** Assuming a 2-week illness destroys a multi-year foundation. Longitudinal data confirms athletes rapidly retrace the steep growth curve upon resumption, returning to previous peak fitness in 4–6 weeks.

---

## Summary Checklist / Decision Table

### Diagnostic Decision Framework for Stalled Adaptations

| Symptom | Probable Cause | Corrective Action |
| :--- | :--- | :--- |
| **FTP flat for $>6$ months despite hard threshold work** | Fractional utilization ceiling reached ($\text{FTP} \approx \text{VO}_2\text{max}$) | Execute 3–4 week block of dedicated $\text{VO}_2\text{max}$ intervals |
| **High peak power, but cannot sustain FTP $>35$ min** | Aerobic base / muscular endurance deficiency | Shift to extensive Sweet Spot/Threshold progressions ($2\times30, 1\times60$) |
| **Gaining $<10\text{W}$ per year after 5 years of training** | Natural late-stage asymptote on current growth curve | Shift focus to durability, repeatability, and tactical race execution |
| **Sudden, unexplained power collapse across all durations** | Chronic autonomic overreaching / under-recovery | Prescribe 7–10 days of active recovery / low Zone 1 riding |

### Coach & Athlete Annual Planning Checklist

* [ ] **Plot Historical Multi-Year FTP:** Log yearly peak FTP values in a spreadsheet and apply a logarithmic trendline to establish the athlete's baseline adaptation slope.
* [ ] **Set Calibrated Annual Targets:** For athletes with $>3$ years of structured training, target realistic $3\text{–}5\%$ annual improvements rather than double-digit expectations.
* [ ] **Plan Post-Offseason Re-Ascent:** Expect the first 8–12 weeks of a new season to retrace prior peaks before breaking new absolute ground.
* [ ] **Rotate Physiological Bottlenecks:** Alternate between raising the ceiling ($\text{VO}_2\text{max}$), extending the floor ($\text{TTE}$ / extensive threshold), and building durability (fatigued work capacity).
* [ ] **Audit Recovery Hygiene:** Before modifying training stimulus to break a plateau, ensure sleep duration, caloric availability, and life stress are fully optimized.
