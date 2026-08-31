---
title: "A Replication Crisis Is a Crisis of Confidence: Statistical Fallacies, Winner's Curse, and Interpreting Exercise Science — Complete Guide"
category: physiology
topics:
  - "FTP"
  - "Durability"
source: "Empirical Cycling Podcast — Kolie Moore & Kyle Hanson (Watts Doc #64)"
author: "Kolie Moore"
date: "2026-05-20"
summary: "A deep dive into the landmark sports science replication project (Murphy et al.), examining why only 28% of top-journal exercise studies fully replicated, deconstructing statistical traps like Winner's Curse and p-hacking, and establishing how coaches should critically interpret scientific literature."
key_takeaways:
  - "In a large-scale replication of top-quartile sports science studies (Murphy et al.), only 28% of original findings met all replication criteria, with replicated effect sizes averaging 25–50% of original published magnitudes."
  - "Underpowered studies (N=10–15) suffer from 'Winner's Curse': an intervention can only achieve statistical significance if random sampling error inflates the effect size far beyond the true population mean."
  - "Meta-analyses do not automatically fix small-sample bias; aggregating 10 studies of N=10 subjects each simply pools 10 studies afflicted by publication bias and inflated effect sizes."
  - "The 'Replication Crisis' is primarily a 'Crisis of Confidence' among practitioners who view published studies as infallible dogma ('the science says') rather than provisional hypotheses within a fallibilist methodology."
  - "Coaches should maintain low prior confidence for novel, single-study performance claims and rely instead on large, convergent bodies of physiological evidence."
---

# A Replication Crisis Is a Crisis of Confidence: Statistical Fallacies, Winner's Curse, and Interpreting Exercise Science — Complete Guide
_Source: Empirical Cycling Podcast — Kolie Moore & Kyle Hanson (Watts Doc #64)_

---

## What Is the Replication Crisis in Exercise Science?

For decades, the field of sports and exercise physiology relied on single, small-cohort laboratory trials ($N = 8\text{–}16$) to establish training and nutritional dogma. In 2023, a landmark multi-laboratory replication initiative led by **Jennifer Murphy and over 40 international collaborators** systematically evaluated the reproducibility of top-tier sports science literature.

```
       Murphy et al. Sports Science Replication Initiative
 ┌─────────────────────────────────────────────────────────────┐
 │ 587 Candidate Studies (Top Quartile Journals, 2016–2021)    │
 └──────────────────────────────┬──────────────────────────────┘
                                │ (Random allocation to qualified labs)
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ 25 Rigorous Direct Replications (BUCSS Powered; Mean N=33)  │
 └──────────────────────────────┬──────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
 [Statistical Sig: 56%]  [Direction Match: 88%]  [Magnitude Match: 36%]
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ OVERALL SUCCESSFUL REPLICATION RATE: 28% (7 of 25 Studies)  │
 └─────────────────────────────────────────────────────────────┘
```

The findings demonstrated that while over half of the studies replicated statistical significance ($p < 0.05$), **only 28% replicated both statistical significance and effect size magnitude**. Furthermore, replicated effect sizes were typically **25% to 50% of the magnitude** reported in the original publications.

---

## Key Statistical Mechanisms & Theoretical Concepts

### 1. Winner's Curse & Regression to the Mean

The mathematical phenomenon of **Winner's Curse** explains why initial exercise studies almost always overestimate performance benefits:

```
                      Winner's Curse in Small Samples
 Probability Density
       ▲
       │             True Population Effect Size (d = 0.25)
       │                       │
       │                   ┌───┴───┐
       │                   │       │
       │               ┌───┴───────┴───┐
       │             ┌─┘               └─┐
       │           ┌─┘                   └─┐
       │         ┌─┘                       └─┐  Statistical Power Detection Cutoff (N=12)
       │       ┌─┘                           └─┐           │
       │     ┌─┘                               └─┐         ▼
       │   ┌─┘                                   └─┐ ┌───────────┐
       │ ┌─┘                                       └─┤ PUBLISHED │ (d = 0.95, p < 0.05)
       └─┴───────────────────────────────────────────┴───────────┴────────► Effect Size (d)
          ◄──────── Non-Significant / File Drawer ────────►
```

#### The Statistical Mechanics:
1. **Detection Threshold:** In an underpowered study ($N = 10\text{–}14$), the minimum detectable effect size required to achieve $p < 0.05$ is massive ($d \ge 0.8\text{–}1.0$).
2. **Sampling Variance:** Due to normal biological noise (sleep, genetics, acute motivation), one random cohort of 10 subjects will randomly exhibit an extraordinary response.
3. **Selective Publication:** Only this statistical outlier achieves $p < 0.05$ and gets published ("wins" the publication race). The 9 other trials showing modest ($d = 0.2$) or null ($d = 0.0$) effects remain unpublished in file drawers.
4. **Regression to the Mean:** When a replication team doubles the sample size ($N = 33$), the standard error shrinks, and the point estimate regresses back toward the true, modest biological reality ($d \approx 0.25$).

---

### 2. Questionable Research Practices (QRPs) in the Literature

Beyond random sampling error, systemic academic incentives foster Questionable Research Practices that distort published outcomes:

```
┌─────────────────────────┬───────────────────────────────────────────┬───────────────────────────────────────────┐
│ Practice                │ Operational Mechanism                     │ Impact on Endurance Coaching              │
├─────────────────────────┼───────────────────────────────────────────┼───────────────────────────────────────────┤
│ **p-Hacking**           │ Manipulating analysis post-data collection│ Produces false positives for acute        │
│                         │ (selective outlier removal, sub-grouping, │ supplements (e.g., ATP pills, mouth       │
│                         │ interim data peeking until $p < 0.05$).   │ rinses, exotic carb ratios).              │
├─────────────────────────┼───────────────────────────────────────────┼───────────────────────────────────────────┤
│ **HARKing**             │ *Hypothesizing After Results are Known*:  │ Confuses serendipitous exploratory        │
│                         │ Presenting an unexpected post-hoc data    │ findings with tested causal models        │
│                         │ anomaly as the primary a priori hypothesis│ (e.g., Tabata anaerobic study O2 deficit).│
├─────────────────────────┼───────────────────────────────────────────┼───────────────────────────────────────────┤
│ **Dose-Dependent**      │ Unstandardized exercise dosing across arms│ Spurious claims of interval superiority   │
│ **Fallacy**             │ (e.g., matching work kilojoules rather    │ that merely reflect unstandardized total  │
│                         │ than internal metabolic time-in-zone).    │ time at VO2 or threshold.                 │
└─────────────────────────┴───────────────────────────────────────────┴───────────────────────────────────────────┘
```

---

### 3. The Fallacy of Meta-Analytic Salvation

A widespread misconception among practitioners is that a **meta-analysis** automatically cures small-sample errors. 

$$\text{Meta-Analysis of 10 Studies with } N=10 \neq \text{One Robust Study of } N=100$$

If 10 published studies on a training modality all suffer from Winner's Curse and publication bias (excess significance), a standard random-effects meta-analysis simply calculates a weighted average of **10 inflated, biased point estimates**. Unless a meta-analysis has access to individual participant data (IPD) and unpublished null trials, it merely formalizes the bias.

---

## Practical Application: How to Read and Apply Science as a Coach

Science is a **method of rigorous inquiry based on fallibilism**, not an immutable body of dogma. Coaches must transition from asking *"What does the science say?"* to asking *"What is the underlying physiological mechanism, what were the study constraints, and how does this align with longitudinal field observations?"*

```
               Coaching Filter for Published Research
 ┌─────────────────────────────────────────────────────────────────────────┐
 │ 1. Evaluate Sample Size & Power (Is N < 20 claiming a massive d > 1.0?) │
 ├─────────────────────────────────────────────────────────────────────────┤
 │ 2. Audit the Exercise Dosing (Was intensity/duration truly standardized?)│
 ├─────────────────────────────────────────────────────────────────────────┤
 │ 3. Check for Convergent Evidence (Decades of physiology vs. 1 paper)   │
 ├─────────────────────────────────────────────────────────────────────────┤
 │ 4. Assign Conservative Bayesian Priors (Hold novel findings loosely)    │
 └─────────────────────────────────────────────────────────────────────────┘
```

### Hierarchy of Scientific Robustness in Endurance Training

```
  High Confidence / Unassailable Principles
  ┌─────────────────────────────────────────────────────────────┐
  │ • Progressive Overload & Specificity                        │
  │ • Extensive Base Volume driving Mitochondrial Density       │
  │ • Quasi-Steady-State Threshold (FTP / MLSS / CP)            │
  │ • Near-Maximal Cardiac Strain driving VO2max Stroke Volume  │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
  Moderate Confidence / Context Dependent
  ┌─────────────────────────────────────────────────────────────┐
  │ • Periodization Architectures (Polarized vs. Pyramidal)     │
  │ • Double Threshold Microcycle Distribution                  │
  │ • Intra-workout Carb Formulations (1:0.8 vs 2:1 ratios)     │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
  Low Confidence / High Skepticism (Winner's Curse Territory)
  ┌─────────────────────────────────────────────────────────────┐
  │ • Novel ergogenic supplements claiming +5% FTP in 2 weeks   │
  │ • Single-session mechanistic signaling (mRNA / p-AMPK)      │
  │ • Proprietary recovery modalities (infrared, acute massage) │
  └─────────────────────────────────────────────────────────────┘
```

---

## Common Pitfalls & Limitations

1. **Monolithic Truth Fallacy:** Quoting a single paper as unassailable proof of a training philosophy, ignoring statistical power and confounding variables.
2. **Nihilistic Rejection ("Nobody Knows Anything"):** Using replication failures to dismiss all scientific inquiry, retreating into purely anecdotal "bro-science" and superstition.
3. **Mechanistic Storytelling:** Assuming that because a workout increases phosphorylation of a signaling kinase in a biopsy, it will automatically translate to faster 40 km time trial performance.
4. **Ignoring the Effective Dose:** Blindly replicating a research interval protocol (e.g., $4 \times 4\text{ min}$ at $95\%\text{ HRmax}$) without adjusting for the athlete's individual cadence, cooling, and anaerobic capacity.

---

## Summary Checklist / Decision Table

### Evaluating a New Training Study: Coach's Decision Matrix

| Study Feature | Green Flag (High Reliability) | Red Flag (High Skepticism) |
| :--- | :--- | :--- |
| **Sample Size** | $N > 30$ with pre-registered power calculation | $N \le 12$ claiming massive effect sizes ($d > 1.2$) |
| **Pre-Registration** | Registered on OSF / ClinicalTrials with locked analysis | Unregistered exploratory protocol with $>15$ outcome metrics |
| **Protocol Dosing** | Anchored to individualized physiological boundaries (TTE/MLSS)| Fixed generic percentages (e.g., fixed $120\%\text{ FTP}$) |
| **Outcome Metric** | Real-world performance (Mean maximal power, TT time) | Intermediate blood surrogate or acute sprint test proxy |
| **Replication Status**| Multi-center replication with consistent directional match | Single isolated finding contradicting 40 years of literature |

### Framework for Integrating Science into Coaching

* [ ] **Anchor in Fundamental Physiology:** Ensure every training prescription targets verified physiological mechanics (cardiac output, capillarization, fiber recruitment).
* [ ] **Discount Novel Acute Claims:** Apply a steep Bayesian discount to any acute nutritional or training "hack" showing revolutionary gains.
* [ ] **Verify in the Field (FAFO):** Treat any scientific protocol as a hypothesis; test it within the athlete's microcycle and observe individual adaptation over 4–8 weeks.
* [ ] **Demand Independent Replication:** Wait for convergent evidence from multiple independent laboratories before restructuring an athlete's macrocycle.
