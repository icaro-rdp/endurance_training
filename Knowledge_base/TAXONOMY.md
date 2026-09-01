# Endurance Training Knowledge Base Taxonomy

This file is the canonical source for Knowledge Base categories, topics, and
source frontmatter. New Knowledge Sources must use only the exact category and topic values
listed here.

---

## Categories & Topics (4-Pillar Taxonomy - 36 Canonical Topics)

### 1. `training`
Training execution, interval protocol design, aerobic base, resistance exercise, biomechanics, ergonomics, and pacing tactics.
- **Topics**:
  - `Zone2_and_endurance_base` (Low-intensity continuous endurance training volume, Zone 2, LIT, LSD, base miles)
  - `Subthreshold_and_tempo` (Sweet Spot 88-94% FTP, Zone 3 tempo, extensive aerobic density)
  - `Threshold_intervals` (Over-unders, 2x20m, threshold repeats, sustained FTP intervals, lactate clearance)
  - `VO2max_and_aerobic_hiit` (Seiler 4x8/4x4, Ronnestad 30/15, fast-start HIIT, decreasing intervals, severe domain intervals)
  - `Sprint_and_anaerobic_intervals` (Sprint Interval Training SIT 15-30s, repeated sprint ability RSA, microbursts)
  - `Strength_and_resistance_training` (Gym heavy resistance training, squats, deadlifts, unilateral/bilateral, concurrent training)
  - `Torque_and_cadence_drills` (Low-cadence torque efforts, SFR, high-cadence spin-ups, neuromuscular pedaling drills)
  - `Pacing_and_execution_dynamics` (Pacing tactics, ERG vs slope mode, RPE auto-regulation, TT/climb power distribution)
  - `Cross_training_and_multisport` (Modality transfer, run-to-bike transfer, swimming, triathlon brick workouts)
  - `Biomechanics_fit_and_equipment` (Bike fit ergonomics, saddle pressure, aerodynamics CdA, rolling resistance Crr, drivetrain friction)

### 2. `physiology`
Underlying biological mechanisms, cardiovascular remodeling, cellular bioenergetics, metabolic thresholds, fatigue etiology, and diagnostic assessment.
- **Topics**:
  - `Cardiovascular_and_hemodynamics` (Stroke volume, eccentric left ventricular hypertrophy, cardiac output, preload, plasma volume)
  - `Mitochondrial_and_cellular_adaptation` (PGC-1alpha, CaMK, AMPK vs mTOR signaling, citrate synthase, fiber type transitions)
  - `Lactate_kinetics_and_metabolism` (MCT1/4 transporters, Brooks lactate shuttle, clearance dynamics, muscular/hepatic oxidation)
  - `Substrate_utilization_and_fat_oxidation` (Beta-oxidation, CPT-1, FAT/CD36, IMTG vs FFA, glycogen depletion, FatMax, MFO, LCHF)
  - `Thresholds_and_metabolic_domains` (3-domain model: moderate/heavy/severe, LT1/VT1, LT2/VT2, MLSS, RCP, OBLA)
  - `Critical_power_and_w_prime` (Hyperbolic power-duration model, Critical Power CP, W', W'bal, Skiba model, Critical Speed)
  - `FTP_and_functional_metrics` (Functional Threshold Power, Time-to-Exhaustion TTE at FTP, fractional utilization, MMP profile)
  - `VO2max_and_aerobic_kinetics` (VO2max limits, phase I/II/III kinetics, time constant tau, VO2 slow component, MAP)
  - `Durability_and_fatigue_mechanisms` (Durability over kJ, central/peripheral fatigue, motor unit recruitment, Henneman size principle)
  - `Autonomic_and_cardiac_monitoring` (Heart rate variability HRV, rMSSD, resting HR, cardiovascular drift, Power:HR decoupling)
  - `Environmental_and_thermal_stress` (Heat acclimation, core temperature kinetics, sweat rate, altitude/hypoxia, EPO, cold stress)
  - `Physiological_testing_and_diagnostics` (Metabolic cart, FatMax testing, lactate step tests, ramp tests, 20-min test, NIRS/SmO2)
  - `Athlete_health_and_exercise_immunology` (Exercise immunology, J-curve, sickness return-to-play, AFib, bone health, female menstrual cycle)

### 3. `nutrition`
Nutritional fueling, intra-workout carbohydrates, hydration/fluid balance, clinical energy availability, micronutrients, and ergogenic supplementation.
- **Topics**:
  - `Carbohydrate_fueling_and_gut_training` (Intra-workout carb rates 30-120g/hr, glucose:fructose 1:0.8/2:1, SGLT1/GLUT5, gut training)
  - `Daily_macronutrient_and_energy_periodization` (Carbohydrate periodization, fuel for work, train-low/sleep-low, protein 1.6-2.2g/kg, MPS)
  - `Hydration_and_electrolyte_balance` (Fluid replacement, sweat rate calculation, sweat sodium concentration, hyponatremia)
  - `Energy_availability_and_reds` (Relative Energy Deficiency in Sport RED-S, Low Energy Availability LEA <30 kcal/kg, endocrine health)
  - `Ergogenic_supplements_and_buffers` (Sodium bicarbonate, beta-alanine, caffeine, dietary nitrates/beetroot, creatine, ketone esters)
  - `Micronutrients_and_biomarkers` (Iron metabolism, serum ferritin, hepcidin, Vitamin D3, antioxidant debate: Vitamin C/E, blood panels)

### 4. `planning`
Periodization models, training intensity distributions, microcycle architecture, workload quantification, tapering, and overtraining management.
- **Topics**:
  - `Periodization_models_and_macrocycles` (Linear, block periodization, reverse, phase potentiation, annual plan ATP, progressive overload)
  - `Training_intensity_distribution` (TID: Polarized 80/20, pyramidal, threshold-centric distribution, session-goal vs time-in-zone)
  - `Microcycle_and_schedule_design` (7-day/10-day microcycles, session sequencing, Norwegian double threshold scheduling, recovery weeks)
  - `Workload_quantification_and_modeling` (PMC: CTL/ATL/TSB, TSS, NP, IF, Banister impulse-response model, TRIMP, mechanical kJ)
  - `Tapering_and_peaking` (Exponential volume reduction 40-60%, intensity/frequency maintenance, taper duration, race openers)
  - `Overtraining_and_recovery_management` (Functional/non-functional overreaching, OTS, sleep architecture, recovery modalities)
  - `Psychology_and_cognitive_performance` (Psychobiological model of endurance, RPE governor, mental fatigue, ACT training, resilience)

---

## Canonical Frontmatter Contract

Every curated Markdown Knowledge Source must begin with a YAML mapping. The
current validator reports a blocking workflow error when any of these minimum
fields is missing or empty:

- `title`
- `category`
- `topics`
- `summary`

Every Knowledge Source must use the standard provenance contract below:

```yaml
---
title: "Document Title"
language: en
category: training
topics:
  - VO2max_and_aerobic_hiit
  - Periodization_models_and_macrocycles
source: "Origin URL or podcast name"
author: "Author or speaker"
date: "YYYY-MM-DD"
summary: "One or two faithful English sentences."
---
```

When directly supported takeaways have been reviewed, add:

```yaml
key_takeaways:
  - "A takeaway directly supported by the source"
```

Rules:

- `language` is exactly `en`; the complete source must be English.
- `category` is exactly one of `training`, `physiology`, `nutrition`, or `planning`.
- Every topic uses the exact spelling and case from this file. Do not introduce
  a near-synonym as a one-off tag.
- `source`, `author`, and `date` record real provenance. A publication date uses
  `YYYY-MM-DD`; do not invent a date or provenance placeholder.
- `key_takeaways` is optional. Omit it when no takeaways have been deliberately
  curated; indexing does not synthesize it.

The passage layer derives `source_type`, repository-relative path,
`source_slug`, passage identifiers and boundaries, citation line ranges, and
size diagnostics. Those values do not belong in source frontmatter.

