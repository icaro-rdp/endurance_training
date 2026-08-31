---
title: "The Relationship Between Size and Power (Allometry & Scaling) — Complete Guide"
category: physiology
topics:
  - "FTP"
  - "VO2max"
  - "Sprint_performance"
  - "Power_vs_HR"
source: "Empirical Cycling Podcast — Kolie Moore & Kyle Hanson (Watts Doc #42)"
author: "Kolie Moore"
date: "2023-01-17"
summary: "A comprehensive analysis of allometric scaling laws in endurance and strength sports, explaining why gaining muscle does not raise aerobic power, how absolute power versus W/kg and W/CdA govern cycling physics, and the physiological basis of the Grand Tour winner phenotype."
key_takeaways:
  - "VO2max is centrally limited by cardiac stroke volume and vascular delivery, not peripheral muscle mass; adding muscular hypertrophy without aerobic training dilutes oxygen delivery and fails to increase FTP."
  - "Allometric scaling reveals that absolute VO2max scales with body mass to the ~0.87–0.94 power, while relative VO2max (mL/kg/min) scales inversely (M^-0.13), giving smaller athletes a natural W/kg advantage and larger athletes a raw wattage advantage."
  - "Muscular force generation scales with cross-sectional area (M^0.67 or 2/3 power), explaining why smaller athletes have higher relative strength-to-weight ratios, while larger athletes produce superior absolute peak sprint power."
  - "On flat terrain, power-to-aerodynamic drag (W/CdA) dominates because frontal surface area scales with M^0.67 while absolute aerobic power scales with M^0.87–0.90, heavily favoring larger, taller riders."
  - "The prototypical Grand Tour GC rider (~180 cm, 65–70 kg) represents the biological sweet spot balancing high absolute aerobic engine size (5.5–6.0+ L/min) with world-class climbing W/kg (>6.0 W/kg)."
---

# The Relationship Between Size and Power (Allometry & Scaling) — Complete Guide
_Source: Empirical Cycling Podcast — Kolie Moore & Kyle Hanson (Watts Doc #42)_

---

## What Is Allometric Scaling in Exercise Physiology?

In cycling and endurance sports, debates frequently arise over whether a rider should prioritize absolute power (Watts), power-to-weight ratio ($\text{W/kg}$), or power-to-aerodynamic-drag ($\text{W/CdA}$). 

**Allometry** is the study of how physiological traits, metabolic rates, and mechanical forces scale with changes in body size. Human physiology does not scale in a simple 1:1 linear fashion:

* **Geometric Scaling ($L^1, L^2, L^3$):** If an organism's linear dimensions ($L$) double, its surface area and cross-sectional area scale with $L^2$ ($4\times$), while its volume and body mass ($M$) scale with $L^3$ ($8\times$).
* **Metabolic Scaling:** Basal metabolic rate (BMR) scales across species to approximately the **$3/4$ power ($M^{0.75}$)** (Kleiber's Law), driven by thermal dissipation constraints and vascular fractal branching networks.
* **Maximal Aerobic Scaling:** In athletic species at maximal exertion, $\text{VO}_2\text{max}$ scales almost linearly with body mass (**$M^{0.87}\text{ to }M^{0.94}$**), because active skeletal muscle accounts for $>90\%$ of total oxygen consumption.

```
 Dimension / Metric      Scaling Factor (Mass M)   Physiological Consequence
 ─────────────────────────────────────────────────────────────────────────────────────────────
 Body Volume / Mass     │ M^1.00 (L^3)            │ Base reference mass
 Muscle Cross-Section   │ M^0.67 (L^2 / 2/3 power)│ Max force & sprint power scaling
 Frontal Surface Area   │ M^0.67 (L^2 / 2/3 power)│ Aerodynamic drag (CdA) scaling
 Absolute VO2max (L/min)│ M^0.87–0.94             │ Aerobic engine size in athletic animals
 Relative VO2max (mL/kg)│ M^-0.13                 │ Relative climbing capacity (favors smaller)
```

---

## Key Physiological Mechanisms / How to Think About It

### 1. Why Gaining Muscle Does Not Increase Aerobic Power

A common intuition among novices is that since muscles produce pedal wattage, building bigger leg muscles in the gym should increase $\text{VO}_2\text{max}$ and FTP. Physiologically, this is incorrect:

* **Central Delivery Limitation:** $\text{VO}_2\text{max}$ is limited centrally by maximum cardiac output ($\dot{Q}_{\text{max}} = \text{HR}_{\text{max}} \times \text{Stroke Volume}$), systemic vascular conductance, and total hemoglobin mass.
* **Contractile Muscle Mass Is Not the Limiter:** Even a 55 kg climber has more than enough cross-sectional muscle area to generate $450\text{W}$ of mechanical force; what they lack is the central cardiovascular engine to supply enough oxygenated blood to sustain it aerobically.
* **The "Dilution" Penalty:** If an athlete adds $5\text{ kg}$ of muscle hypertrophy without a commensurate increase in cardiac stroke volume, the heart must now distribute the same finite oxygen supply across a larger vascular bed, reducing per-gram tissue perfusion and lowering relative $\text{W/kg}$.

```
 [Left Ventricle: Stroke Volume (~180–200 mL)] ──► Fixed Central Cardiac Output (~35–40 L/min)
                                                             │
                    ┌────────────────────────────────────────┴────────────────────────────────────────┐
                    ▼                                                                                 ▼
     [Slim Endurance Muscle (65 kg)]                                                   [Hypertrophied Muscle (80 kg)]
     High capillary-to-fiber ratio;                                                    Same oxygen distributed across larger
     Maximal per-gram oxygen extraction;                                               tissue volume; lower relative VO2max;
     High relative W/kg.                                                               Excessive non-aerobic weight penalty.
```

### 2. Force vs. Aerobic Scaling: The Strength-to-Weight Divergence

* **Maximal Force Generation:** Muscular tension depends strictly on the number of actin-myosin cross-bridges arranged in parallel, which is proportional to **physiological cross-sectional area (PCSA / $M^{0.67}$)**.
* **The Weightlifting Reality:** In Olympic weightlifting and powerlifting, lighter weight classes lift far higher multiples of their body weight than super-heavyweights (e.g., a 60 kg lifter clean-and-jerking $2.8\times$ body weight vs. a 150 kg lifter clean-and-jerking $1.7\times$ body weight).
* **Track Sprinting vs. Endurance Climbing:**
  * **Track Sprinters:** Require massive cross-sectional area to generate $2,000\text{–}2,500\text{W}$ peak neuromuscular power. The high mass is tolerated on a flat velodrome because gravity is negligible.
  * **Road Climbers:** Require maximal aerobic power-to-weight ($\text{W/kg}$). Hypertrophy is actively suppressed to preserve cardiovascular density.

### 3. Cycling Physics: W/kg vs. W/CdA Scaling

```
 FLAT TERRAIN (Dominated by W / CdA):
 ──────────────────────────────────────────────────────────────────────────
 85 kg Rider: 420W FTP | CdA: 0.24 m² ──► 420 / 0.24 = 1,750 W/m² (Fastest)
 60 kg Rider: 310W FTP | CdA: 0.20 m² ──► 310 / 0.20 = 1,550 W/m² (Gapped)

 STEEP CLIMBING (Dominated by W / kg):
 ──────────────────────────────────────────────────────────────────────────
 60 kg Rider: 310W FTP ──► 310 / 60 = 5.17 W/kg (Climbs faster)
 85 kg Rider: 420W FTP ──► 420 / 85 = 4.94 W/kg (Dropped on 8% grade)
```

* **Flat Roads and Flat Time Trials:** Aerodynamic drag ($\text{CdA}$) increases with body surface area ($M^{0.67}$). Because aerobic power scales faster ($M^{0.87\text{–}0.90}$), **larger riders inherently produce higher $\text{W/CdA}$ ratios** and travel faster on flat terrain for the same relative fitness.
* **Steep Climbs (>6–8% grade):** Gravitational resistance scales linearly with total system mass ($M^{1.00}$). Because relative $\text{VO}_2\text{max}$ scales inversely ($M^{-0.13}$), **smaller riders naturally attain higher $\text{W/kg}$**, out-climbing larger riders on steep gradients.

### 4. The Grand Tour GC Champion Phenotype

Historical and physiological analysis of modern Grand Tour winners reveals a remarkably consistent morphological convergence:

* **Height:** $\sim 178\text{ to }184\text{ cm}$ ($5'10"\text{ to }6'0"$).
* **Body Mass:** $\sim 65\text{ to }70\text{ kg}$ ($143\text{ to }154\text{ lbs}$).
* **Physiological Balance:** This phenotype provides the optimal intersection between:
  1. A large absolute thoracic cage and heart capable of generating **$5.5\text{ to }6.0+\text{ L/min}$ absolute $\text{VO}_2\text{max}$** (essential for flat time trials and high tempo).
  2. Extremely low body fat and minimal non-functional upper-body mass, yielding **$>6.0\text{ W/kg}$ threshold** for high-altitude mountain passes.

---

## Practical Application & Prescriptions

### 1. Weight Loss and the "FTP Drop" Phenomenon

When endurance athletes attempt aggressive calorie restriction ("crash dieting") to improve $\text{W/kg}$, they frequently experience a severe drop in absolute FTP:

* **Why FTP Drops on Severe Deficits:**
  1. **Intramuscular Glycogen Depletion:** Low resting glycogen impairs sarcoplasmic reticulum calcium kinetics and reduces glycolytic flux.
  2. **Thyroid & Autonomic Downregulation:** Triiodothyronine ($\text{T}_3$) and sympathetic output drop, inducing chronic lethargy and high RPE.
  3. **Loss of Contractile Protein:** In severe deficits, gluconeogenesis metabolizes branched-chain amino acids from active muscle tissue.
* **The Sustainable Weight Management Protocol:**
  * Target a modest caloric deficit of **300 to 500 kcal/day** ($0.3\text{ to }0.5\text{ kg/week}$ loss max).
  * **Always Fuel the Work:** Ingest full carbohydrate requirements on the bike ($60\text{–}90\text{ g/hr}$) during workouts; create the deficit exclusively off the bike from resting meals.
  * Monitor threshold power weekly: if FTP drops by $>3\%$, halt the deficit immediately and return to isocaloric baseline.

### 2. Discipline-Specific Morphology & Training Focus

```
 Discipline          Primary Mechanical Limiter  Morphological Focus        Key Training Modality
 ────────────────────────────────────────────────────────────────────────────────────────────────
 Flat Time Trial     W / CdA (Aero Drag)        Taller / Absolute Watts    Sustained Threshold / Sweet Spot
 Criterium / Track   Peak Watts & W'            Mesomorphic / High Torque  Sprint RFD / Microbursts
 Mountain Climbing   W / kg (Gravity)           Ectomorphic / Ultra-Lean   Extensive Threshold / Z2 Base
 Rolling Road Race   W / kg + Repeatability     All-Round GC Phenotype     Pyramidal Base + Extensive FTP
```

---

## Common Pitfalls & Limitations

> [!WARNING]
> **The Vanity W/kg Trap:** Chasing an arbitrary $\text{W/kg}$ number through chronic under-eating leads to Relative Energy Deficiency in Sport (RED-S), bone mineral density loss, hormonal suppression, and ruined durability. A healthy 70 kg rider with 380W (5.4 W/kg) will consistently outperform an under-fueled, fragile 60 kg rider with 330W (5.5 W/kg) across a 5-hour road race.

1. **Attempting to Build "Aerobic Muscle" with Heavy Lifting:** Heavy resistance training improves tendon stiffness, neuromuscular rate of force development (RFD), and sprint power, but it will never increase $\text{VO}_2\text{max}$ or threshold wattage.
2. **Comparing Watts Directly Across Body Sizes:** Expecting a 52 kg female climber to produce the same raw wattage as an 80 kg male rouleur demonstrates ignorance of allometric scaling. Always evaluate athletes relative to their discipline-specific power-to-drag or power-to-mass requirements.
3. **Sacrificing Flat Speed for Marginal Climbing Gains:** Dropping body weight excessively can reduce total plasma volume and cardiac filling, degrading flat time-trial wattage far more than the minor benefit gained on moderate climbs.

---

## Summary Checklist / Decision Table

### Allometric Scaling Laws Summary

| Biological Metric | Scaling Exponent ($M^x$) | Advantage Favors | Key Sporting Application |
| :--- | :--- | :--- | :--- |
| **Basal Metabolic Rate** | $\approx M^{0.75}$ | Smaller Organisms | Daily caloric maintenance per kg is higher in smaller humans. |
| **Max Strength / Force** | $\approx M^{0.67}$ | Smaller (Relative) / Larger (Absolute) | Relative strength (lifting multiple of BW) favors smaller athletes; raw sprint force favors larger. |
| **Aerodynamic Drag ($\text{CdA}$)** | $\approx M^{0.67}$ | Larger Riders (W/CdA ratio) | Flat TTs, team pursuits, and bunch sprints favor larger riders with high raw power. |
| **Absolute $\text{VO}_2\text{max}$** | $\approx M^{0.87\text{–}0.94}$ | Larger Riders | Raw oxygen delivery capacity scales near-linearly in athletic bodies. |
| **Relative $\text{VO}_2\text{max}$ ($\text{W/kg}$)** | $\approx M^{-0.13}$ | Smaller Riders | Steep mountain climbs (>7% grade) favor light, small-stature specialists. |

### Coach & Athlete Action Checklist

* [ ] **Identify the Event Demands:** Determine whether the goal event is governed primarily by $\text{W/CdA}$ (flat TT/crit) or $\text{W/kg}$ (steep climbing/Everesting).
* [ ] **Do Not Use Strength Training for Aerobic Gains:** Use lifting strictly for neuromuscular force, injury prevention, and sprint RFD; build aerobic capacity via high-volume cycling and threshold intervals.
* [ ] **Preserve Absolute Engine Size During Fat Loss:** Ensure on-the-bike fueling (60–90g/hr carbs) remains high during weight loss phases to avoid losing functional threshold power.
* [ ] **Target Healthy Body Composition Naturally:** Prioritize consistent high training volume and unprocessed nutrient density over extreme caloric restriction.
