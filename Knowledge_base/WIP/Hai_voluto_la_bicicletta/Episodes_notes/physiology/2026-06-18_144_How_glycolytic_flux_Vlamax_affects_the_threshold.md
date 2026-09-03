---
title: '144: How Glycolytic Flux (VLamax) Affects the Anaerobic Threshold'
language: en
category: physiology
topics:
- Lactate_kinetics_and_metabolism
- FTP_and_functional_metrics
- Thresholds_and_metabolic_domains
- Substrate_utilization_and_fat_oxidation
- Physiological_testing_and_diagnostics
source: https://open.spotify.com/episode/7oYxUNqNXGK4y73NiQE6yO
author: Daniele Bazzana, Stefano Nardelli
date: '2026-06-18'
summary: Examines the mathematical bioenergetics of Mader's model, illustrating how maximum glycolytic rate (VLamax) interacts with VO2max to govern lactate accumulation, substrate partitioning, and anaerobic threshold power.
---

# 144: How Glycolytic Flux (VLamax) Affects the Anaerobic Threshold

## Overview and Physiological Definition

The Maximal Lactate Steady State (MLSS), Functional Threshold Power (FTP), or second lactate threshold (LT2) is widely understood as the highest power output where lactate production matches lactate clearance. However, threshold power is not an independent physiological entity; it is governed by the dynamic equilibrium between two opposing bioenergetic engines:

1. **Aerobic Power ($\dot{V}O_{2\text{max}}$):** The maximum capacity of the mitochondrial oxidative system to consume oxygen and oxidize substrates (fat and lactate/pyruvate).
2. **Glycolytic Power ($V_{La\text{max}}$):** The maximum rate of lactate production by the anaerobic glycolytic system in skeletal muscle (expressed in $\text{mmol}\cdot\text{L}^{-1}\cdot\text{s}^{-1}$).

Formalized in the metabolic models of **Alois Mader** and **Ulrich Hartmann**, the interaction between $\dot{V}O_{2\text{max}}$ and $V_{La\text{max}}$ explains why two athletes with identical $\dot{V}O_{2\text{max}}$ scores can possess vastly different threshold powers, carbohydrate combustion rates, and fatigue profiles.

```
       +-------------------------------------------------------------+
       |               THE MADER BIOENERGETIC EQUILIBRIUM            |
       +-------------------------------------------------------------+
       |                                                             |
       |      GLYCOLYTIC SYSTEM                 OXIDATIVE SYSTEM     |
       |     Max Glycolytic Flux               Max Aerobic Capacity  |
       |          (VLamax)                           (VO2max)        |
       |             \                                 /             |
       |              \                               /              |
       |               v                             v               |
       |          Lactate/Pyruvate               Mitochondrial       |
       |             Production                  Combustion Rate     |
       |                      \                 /                    |
       |                       \               /                     |
       |                        v             v                      |
       |                   +=======================+                 |
       |                   |  ANAEROBIC THRESHOLD  |                 |
       |                   |   (Rate In = Rate Out)|                 |
       |                   +=======================+                 |
       +-------------------------------------------------------------+
```

---

## 1. The Mathematical and Physiological Mechanism of VLamax

### Lactate Kinetics as a Balancing Act
- At any submaximal workload, pyruvate is produced via glycolysis. If the glycolytic flux exceeds the mitochondrial pyruvate dehydrogenase (PDH) entry rate, excess pyruvate is converted to lactate via lactate dehydrogenase (LDH).
- Lactate is not a waste product; it is a vital energy shuttle (Brooks Lactate Shuttle). It is transported via monocarboxylate transporters (MCT1 into oxidative fibers/mitochondria, MCT4 out of glycolytic fibers) and oxidized in adjacent Type I fibers, the heart, and the liver (Cori cycle).

### The Mathematical Impact of High vs. Low VLamax
- **High $V_{La\text{max}}$ (>0.6–0.9 mmol/L/s):** The athlete has high glycolytic enzyme capacity (phosphofructokinase, LDH). Even at low submaximal intensities, glycolysis produces substantial pyruvate/lactate. This "floods" the oxidative system early, causing the anaerobic threshold to occur at a **lower percentage of $\dot{V}O_{2\text{max}}$** (e.g., 65–72%).
- **Low $V_{La\text{max}}$ (<0.2–0.4 mmol/L/s):** Glycolytic flux is suppressed. At submaximal powers, lactate production is minimal, allowing the athlete to sustain power up to **85–90% of $\dot{V}O_{2\text{max}}$** before lactate production surpasses oxidative clearance capacity.

```
High VLamax Athlete (Sprinter):
VO2max: 70 mL/kg/min | VLamax: 0.8 mmol/L/s ---> Threshold: 280 W (68% VO2max) | High Carb Burn

Low VLamax Athlete (Climber/TT):
VO2max: 70 mL/kg/min | VLamax: 0.3 mmol/L/s ---> Threshold: 360 W (86% VO2max) | High Fat Oxidation
```

---

## 2. Athlete Phenotypes and Event Demands

Different cycling disciplines require specific tuning of the $\dot{V}O_{2\text{max}}$ to $V_{La\text{max}}$ ratio:

| Discipline | Target Phenotype | Optimal $V_{La\text{max}}$ | Target $\dot{V}O_{2\text{max}}$ | Physiological Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Grand Tour Climber / Time Trialist** | Diesel / High Fractional Utilizer | **Low** (0.20–0.35 mmol/L/s) | **Very High** (>80 mL/kg) | Maximize threshold watts and fat oxidation; spare glycogen for final climbs |
| **Criterium Racer / Cyclocross** | Puncheur / Anaerobic Engine | **Moderate** (0.45–0.60 mmol/L/s) | **High** (>72 mL/kg) | High threshold combined with sufficient $W'$ recharge and repeated surge power |
| **Track Sprinter / Road Sprinter** | Explosive / Glycolytic Monster | **Very High** (>0.75–1.0 mmol/L/s) | **Moderate** (60–68 mL/kg) | Maximum peak power (>1500 W) and explosive 15–30s kinetic acceleration |

---

## 3. Training Methodologies to Manipulate VLamax

### How to Reduce VLamax (Increasing Threshold & Fat Oxidation)
1. **High-Volume Low-Intensity Endurance (Zone 2):** Stimulates mitochondrial biogenesis and capillary density, down-regulating glycolytic enzyme expression and shifting substrate reliance toward beta-oxidation.
2. **Low-Cadence High-Torque Intervals (SFR / Big Gear Tempos):** 40–60 RPM at Sweet Spot / Low Threshold forces maximal motor unit tension without rapid kinetic cycling, inhibiting glycolytic enzymes and recruiting oxidative pathways.
3. **Extensive Sweet Spot & Threshold Repeats ($2 \times 20\text{m}$, $3 \times 15\text{m}$):** Sustained steady-state lactate accumulation trains MCT1 transporters to up-regulate oxidative lactate clearance.
4. **Targeted Carbohydrate Periodization (Train-Low / Fasted):** Exercising with reduced muscle glycogen down-regulates pyruvate dehydrogenase (PDH) kinase and suppresses glycolytic flux.

### How to Increase VLamax (Developing Sprint Power and Anaerobic Capacity)
1. **Sprint Interval Training (SIT):** All-out maximal efforts of 10–20 seconds with full recovery (>3–5 minutes) maximize phosphagen and glycolytic flux, stimulating PFK activity.
2. **Heavy Resistance Strength Training:** High-load squats and explosive leg press movements recruit and hypertrophy Type IIx glycolytic muscle fibers.

---

## Key Takeaways and Practical Recommendations

- **Threshold Is a Balance Point:** Anaerobic threshold is governed by the ratio of aerobic oxidative capacity ($\dot{V}O_{2\text{max}}$) to glycolytic power ($V_{La\text{max}}$).
- **Lowering $V_{La\text{max}}$ Raises Threshold:** For endurance events and time trials, reducing $V_{La\text{max}}$ allows an athlete to utilize a higher fraction of their $\dot{V}O_{2\text{max}}$, directly elevating FTP and sparing glycogen.
- **Match Phenotype to Racing Demands:** A pure climber needs a low $V_{La\text{max}}$ to maximize threshold, whereas a criterium racer or sprinter needs moderate-to-high $V_{La\text{max}}$ to execute race-winning anaerobic surges.
- **Train Specifically:** Use high-volume Zone 2, low-cadence torque work, and extensive threshold intervals to lower $V_{La\text{max}}$; utilize maximal sprints and heavy gym resistance training to increase it.
