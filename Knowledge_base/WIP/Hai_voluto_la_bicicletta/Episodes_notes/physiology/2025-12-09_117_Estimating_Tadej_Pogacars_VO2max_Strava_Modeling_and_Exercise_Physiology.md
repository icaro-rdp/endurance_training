---
title: '117: Estimating Tadej Pogačar''s VO2max: Strava Modeling and Exercise Physiology'
language: en
category: physiology
topics:
- VO2max_and_aerobic_kinetics
- Critical_power_and_w_prime
- Physiological_testing_and_diagnostics
- Durability_and_fatigue_mechanisms
- Biomechanics_fit_and_equipment
source: https://open.spotify.com/episode/33qTONC85cVdB0LALngSbW
author: Daniele Bazzana, Stefano Nardelli
date: '2025-12-09'
summary: Analyzes Ole Kristian Berg's "Tour de Physiology" mathematical model estimating Tadej Pogačar's VO2max from public Strava climbing data, evaluating mechanical power equations, gross efficiency assumptions, and historical performance comparisons.
---
# 117: Estimating Tadej Pogačar's VO2max: Strava Modeling and Exercise Physiology

## Overview and Context

Tadej Pogačar's performances in recent Grand Tours—such as shattering historic climbing records on the *Plateau de Beille*, *San Luca*, and *Isola 2000*—have ignited intense debate in the sports science community. Public curiosity has centered on what physiological values (specifically $	ext{VO}_2	ext{max}$ and sustainable W/kg) are required to produce such record-breaking climbing times.

This episode analyzes the notable publication *"Tour de Physiology"* by Norwegian researcher **Ole Kristian Berg**. Berg developed a comprehensive mathematical model using public GPS and segment timing data from Strava to estimate Pogačar's mechanical power output and calculate his theoretical $	ext{VO}_2	ext{max}$. The hosts break down the physics of the model, examine the physiological plausibility of the results, and contextualize modern climbing speeds against historical benchmarks.

---

## 1. Physics and Mathematics of the Climbing Power Model

To estimate power output from GPS segment times, Berg's model solves the fundamental equation of cycling propulsion:

$$P_{total} = P_{gravity} + P_{rolling} + P_{aero} + P_{drivetrain}$$

### Component Breakdown:
1. **Gravitational Power ($P_{gravity}$):**
   $$P_{gravity} = (m_{rider} + m_{bike}) \cdot g \cdot \sin(	heta) \cdot v$$
   On steep gradients ($> 7	ext{--}8\%$), gravitational resistance accounts for $85	ext{--}90\%$ of total power output.
2. **Rolling Resistance ($P_{rolling}$):**
   $$P_{rolling} = C_{rr} \cdot (m_{rider} + m_{bike}) \cdot g \cdot \cos(	heta) \cdot v$$
   Modern tubeless tires on smooth asphalt have lowered $C_{rr}$ to $pprox 0.0025	ext{--}0.0035$.
3. **Aerodynamic Drag ($P_{aero}$):**
   $$P_{aero} = rac{1}{2} \cdot ho \cdot C_d A \cdot (v + v_{wind})^2 \cdot v$$
   Even uphill at $22	ext{--}25 	ext{ km/h}$, drafting in a mountain lead-out train saves $15	ext{--}30 	ext{ watts}$.
4. **Drivetrain Friction Losses:** Typically estimated at $2	ext{--}3\%$ for clean, waxed 12-speed chains.

---

## 2. Converting Mechanical Watts to $	ext{VO}_2	ext{max}$

Once external mechanical power ($P_{ext}$) is estimated, calculating oxygen consumption requires converting watts to metabolic energy expenditure:

$$	ext{VO}_2 = rac{P_{ext}}{	ext{Gross Efficiency} 	imes k_{cal\_to\_J}} 	imes 1000$$

- **Gross Mechanical Efficiency (GE):** Human cycling efficiency typically ranges between **21% and 24%** (averaging $pprox 22.5\%$ in elite cyclists).
- **Fractional Utilization Assumption:** On a 35–40 minute climb like Plateau de Beille, an elite rider operates at approximately **85 to 88% of $	ext{VO}_2	ext{max}$**.
- **Model Output:** Applying these equations to Pogačar's estimated $pprox 6.8	ext{--}7.0 	ext{ W/kg}$ for $pprox 39 	ext{ minutes}$ yields an estimated $	ext{VO}_2	ext{max}$ in the range of **88 to 92+ mL/kg/min**.

---

## 3. Historical Comparisons: Modern vs. 1990s Benchmarks

- **Comparison with Oskar Svendsen (96.7 mL/kg/min):** The highest recorded lab $	ext{VO}_2	ext{max}$ in cycling history belongs to former junior world time trial champion Oskar Svendsen ($96.7 	ext{ mL/kg/min}$). Pogačar's estimated values ($88	ext{--}92 	ext{ mL/kg/min}$) sit comfortably within the upper echelon of known elite physiology.
- **Breaking 1990s Climb Records:** Pogačar lowering Marco Pantani's 1998 Plateau de Beille record by over 3.5 minutes is explained by a convergence of factors:
  - Higher baseline $	ext{VO}_2	ext{max}$ and fractional utilization supported by $120 	ext{ g/hr}$ carbohydrate fueling.
  - High-speed team pacing trains providing continuous aerodynamic drafting on 6–8% slopes.
  - Advanced bicycle tech: $6.8 	ext{ kg}$ bikes, optimized tubeless rolling resistance, aerodynamic cockpits, and ceramic/waxed drivetrains saving 20–30 total watts compared to 1990s equipment.
  - Steady pacing dynamics vs. erratic attack-and-stall surges of the 1990s.

---

## 4. Methodological Limitations of Strava-Based Modeling

The hosts highlight key confounding variables in external mathematical modeling:
- **Rider Mass Uncertainty:** Small errors in assumed rider weight ($\pm 1	ext{--}2 	ext{ kg}$) or bike/kit weight significantly alter calculated W/kg.
- **Wind Vector Assumptions:** Mountain valleys generate localized microclimates; headwind vs. tailwind can alter power requirements by 20+ watts.
- **Variable Drafting Benefits:** Accurately quantifying the exact drag reduction from sitting behind teammates requires computational fluid dynamics (CFD) that Strava data cannot capture.

---

## Key Takeaways and Practical Recommendations

- **Elite Physiology Confirmed:** Pogačar's climbing performances correspond to a theoretical $	ext{VO}_2	ext{max}$ between 88 and 92+ mL/kg/min operating at 85–88% fractional utilization.
- **Performance is Multifactorial:** Modern record-breaking climbing speeds reflect the combined impact of elite physiology, advanced intra-race nutrition (120 g/hr), aerodynamic drafting in mountain trains, and modern low-$C_{rr}$ equipment.
- **Respect Model Assumptions:** Strava-based power estimates are valuable approximations, but must be interpreted with caution due to unmeasured wind, drafting, and exact mass variables.
