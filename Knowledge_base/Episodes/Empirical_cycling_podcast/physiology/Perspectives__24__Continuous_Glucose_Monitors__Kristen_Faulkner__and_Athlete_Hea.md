---
title: Continuous Glucose Monitors (CGMs), Athlete Health, and RED-S — Complete Guide
category: physiology
topics:
- Lactate_kinetics_and_metabolism
- Substrate_utilization_and_fat_oxidation
- Mitochondrial_and_cellular_adaptation
- Cardiovascular_and_hemodynamics
- Athlete_health_and_exercise_immunology
- Energy_availability_and_reds
- Hydration_and_electrolyte_balance
source: 'Empirical Cycling Podcast — Kolie Moore, Dr. Traci Carson, Dr. Namrita Brooke,
  & Dr. Fabiano Araujo (Perspectives #24)'
author: Kolie Moore
date: '2023-03-30'
summary: The document delves into the physiological mechanisms of glucose dynamics,
  including lactate kinetics, substrate utilization, and energy availability, highlighting
  the complexities of RED-S and the limitations of CGMs in monitoring athlete health.
key_takeaways:
- CGMs measure interstitial fluid glucose—not blood glucose—introducing a 5–15 minute
  physiological lag time that renders reactive in-race fueling adjustments largely
  ineffective.
- Interstitial glucose reflects a dynamic multi-compartment equilibrium (gastric emptying,
  splanchnic absorption, hepatic output, and GLUT4 muscle uptake) and does not measure
  intramuscular or hepatic glycogen stores.
- CGMs confer no direct competitive performance advantage in races; structured, proactive
  carbohydrate ingestion (60–100+ g/hr) vastly outperforms reactive biofeedback.
- Low Energy Availability (LEA) and RED-S disrupt neuroendocrine signaling and ovarian
  function; while chronic LEA lowers baseline glucose, CGMs are not a validated diagnostic
  proxy for energy availability.
- Misinterpreting acute postprandial glucose excursions can induce 'glucorexia' and
  orthorexic food avoidance, leading athletes to eliminate vital high-glycemic carbohydrates
  necessary for glycogen replenishment.
---
# Continuous Glucose Monitors (CGMs), Athlete Health, and RED-S — Complete Guide
_Source: Empirical Cycling Podcast — Kolie Moore, Dr. Traci Carson, Dr. Namrita Brooke, & Dr. Fabiano Araujo (Perspectives #24)_

---

## What Are Continuous Glucose Monitors (CGMs) in Endurance Sport?

**Continuous Glucose Monitors (CGMs)** are wearable biosensors featuring a subcutaneous filament that measures glucose concentrations in **interstitial fluid** ($ISF$) rather than capillary or arterial blood.

The commercialization of CGMs for non-diabetic endurance athletes—highlighted by Kristen Faulkner’s 2023 Strade Bianche disqualification under UCI Article 1.3.006—sparked intense debate regarding competitive advantage, metabolic monitoring, and female athlete health.

```
       ┌────────────────────────────────────────────────────────────┐
       │             CONTINUOUS GLUCOSE MONITORING FLUX             │
       └─────────────────────────────┬──────────────────────────────┘
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           ▼                                                   ▼
┌─────────────────────────┐                         ┌─────────────────────────┐
│ Blood Compartment       │                         │ Interstitial Fluid (ISF)│
│  • Hepatic Output       │    Diffusion Gradient   │  • Subcutaneous Sensor  │
│  • Exogenous Gut CHO    │ ──────────────────────► │  • 5–15 min Time Lag    │
│  • GLUT4 Muscle Uptake  │  (Capillary Clearance)  │  • Interstitial Reading │
└─────────────────────────┘                         └─────────────────────────┘
```

---

## Key Physiological Mechanisms / How to Think About It

### 1. Interstitial Fluid vs. Blood Glucose Dynamics & Time Lag

CGM readings represent a delayed mathematical reflection of systemic vascular glucose:
* **The Diffusion Barrier:** Glucose must exit the capillary endothelium into the interstitial space via passive and facilitated diffusion.
* **The 5–15 Minute Lag:** During rapid transitions in glycemic flux (e.g., consuming a concentrated maltodextrin/fructose gel, or initiating a maximal 400W anaerobic attack), interstitial glucose lags arterial blood glucose by **5 to 15 minutes**.
* **Failure of Reactive In-Race Pacing:** If an athlete waits for a CGM to alert them of hypoglycemia during a race, intramuscular glycogen depletion and neuroglycopenia have already occurred. Proactive, clock-based carbohydrate delivery remains the physiological gold standard.

```
  [Gut: Ingestion of Gel] ──► [Blood: Rapid Glucose Spike] ──► [ISF: 5-15 min Lag on CGM]
                                      │
                                      ▼
                      [Muscle: GLUT4 Rapid Translocation]
```

---

### 2. The Multi-Compartment Glucose Pool & Glycogen Blindness

A single interstitial glucose metric cannot distinguish between competing physiological sources and sinks:
* **Inputs (Appearance Rates, $R_a$):** Exogenous carbohydrate absorption (governed by gastric emptying rate, intestinal SGLT1/GLUT5 transport) and endogenous hepatic glycogenolysis / gluconeogenesis.
* **Outputs (Disappearance Rates, $R_d$):** Skeletal muscle glucose uptake via contraction-mediated GLUT4 translocation, non-active tissue uptake, and central nervous system consumption.
* **Glycogen Independence:** An athlete can have normal interstitial glucose readings while being virtually depleted of intramuscular glycogen, because the liver maintains circulating blood glucose homeostatically until catastrophic collapse.

```
                  ┌─────────────────────────────────────────┐
                  │    TOTAL SYSTEMIC GLUCOSE EQUILIBRIUM   │
                  └────────────────────┬────────────────────┘
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
┌───────────────────────────┐                         ┌───────────────────────────┐
│ Rate of Appearance (Ra)   │                         │ Rate of Disappearance (Rd)│
│  • Intestinal Absorption  │     ISF Equilibrium     │  • Active Muscle Uptake   │
│  • Hepatic Glycogenolysis │ ◄─────────────────────► │  • Non-Contractile Tissue │
│  • Gluconeogenesis        │                         │  • Brain & CNS Extraction │
└───────────────────────────┘                         └───────────────────────────┘
```

---

### 3. Low Energy Availability (LEA), RED-S, and Neuroendocrine Disruption

**Relative Energy Deficiency in Sport (RED-S)** occurs when residual energy availability falls below critical thresholds:
$$\text{Energy Availability (EA)} = \frac{\text{Energy Intake (kcal)} - \text{Exercise Energy Expenditure (kcal)}}{\text{Fat-Free Mass (FFM in kg)}} < 30\text{ kcal/kg FFM/day}$$

* **Endocrine Cascades:** Chronic LEA blunts gonadotropin-releasing hormone (GnRH) pulsatility from the hypothalamus, suppressing luteinizing hormone (LH), follicle-stimulating hormone (FSH), and estradiol, leading to **Functional Hypothalamic Amenorrhea (FHA)** and accelerated bone mineral density loss.
* **Metabolic Suppression:** Baseline fasting blood glucose and triiodothyronine ($T_3$) decline to conserve energetic substrate.
* **CGM Limitations in RED-S:** While tracking glucose can assist an athlete in recognizing erratic eating patterns, a CGM **cannot** calculate total daily energy availability or replace a multi-day dietary and clinical metabolic panel.

---

### 4. The Psychological Pitfall: "Glucorexia" and Carbohydrate Phobia

The non-contextual use of CGMs among healthy endurance athletes introduces severe behavioral risks:
* **The "Flatline" Fallacy:** Marketing from metabolic health apps often promotes "flattening the glucose curve." In endurance athletes, postprandial glucose spikes following high-carbohydrate meals are normal, physiological, and necessary to drive insulin-mediated glycogen supercompensation.
* **Carbohydrate Restriction (Orthorexia):** Athletes viewing acute postprandial spikes may erroneously eliminate oats, rice, potatoes, and sports drinks in favor of fats and proteins, directly precipitating glycogen depletion, elevated cortisol, and LEA.

---

## Practical Application & Prescriptions

### 1. Legitimate Use Cases for CGMs in Endurance Athletes

```
  Scenario / Context           Clinical & Performance Utility         Prescriptive Action
  ────────────────────────────────────────────────────────────────────────────────────────
  Pre-Diabetes / Insulin Dys. │ High utility; reveals severe spikes   │ Medical dietary tuning
  Nocturnal Hypoglycemia      │ High utility; identifies sleep crashes│ Pre-bed complex CHO/protein
  24/7 Off-Bike Habit Audit   │ Moderate utility; reveals meal skips  │ Implement regular meal timing
  In-Race Fueling Decisions   │ Low / Detrimental utility (Lag time)  │ Rely on planned 60–90g CHO/hr
```

---

### 2. Proactive In-Race Fueling vs. Reactive CGM Chasing

* **Fixed Hourly Ingestion:** Consume 60–100g of 1:0.8 maltodextrin-to-fructose carbohydrate per hour on a strict 15–20 minute timer regardless of instantaneous CGM readings.
* **Environmental Adjustments:** In hot conditions ($>30^\circ\text{C}$), gastric emptying slows; adjust drink mix osmolality downward (hypotonic formulations) rather than adjusting carbohydrate targets based on delayed CGM feedback.

---

## Common Pitfalls & Limitations

1. **Relying on CGMs for In-Race Nutrition:** Trying to "eat to the sensor," which guarantees under-fueling during the initial 60 minutes and delayed reaction to energy deficits.
2. **Confusing ISF Glucose with Muscle Glycogen:** Believing high glucose readings indicate fully saturated muscle glycogen tanks.
3. **Fearing Post-Workout Carbohydrate Spikes:** Restricting recovery carbohydrate intake due to sharp post-meal glycemic elevations.
4. **Treating CGMs as an All-in-One RED-S Fix:** Assuming that maintaining normal daytime glucose levels guarantees protection against low energy availability and endocrine disruption.

---

## Summary Checklist / Decision Table

### CGM & Fueling Diagnostic Matrix

| Metric / Tool | Flawed Interpretation | Physiologically Grounded Reality |
| :--- | :--- | :--- |
| **In-Race Glucose Sensor** | "Sensor shows 120 mg/dL, so I don't need to eat yet." | Intramuscular glycogen is draining; adhere to scheduled 60–90g CHO/hr. |
| **Post-Meal Glucose Rise** | "Oatmeal spiked my glucose to 160 mg/dL; oats are toxic." | Normal postprandial glycemic response driving insulin and glycogen storage. |
| **Nocturnal Glucose Drops** | "Low night glucose is good for fat oxidation." | Nocturnal hypoglycemia triggers cortisol surges and impairs deep sleep. |
| **RED-S Assessment** | "My CGM is steady, so I cannot have low energy availability." | LEA requires calculating kcal/kg FFM/day and evaluating clinical hormones. |
| **Data Integration** | Evaluating CGM in isolation without power files | Contextualize glucose against power files, cadence, temperature, and food logs. |
