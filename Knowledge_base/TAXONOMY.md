# Endurance Training Knowledge Base Taxonomy

This file is the canonical source for Knowledge Base categories, topics, and
source frontmatter. New Knowledge Sources must use only the exact category and topic values
listed here.

---

## Categories & Topics (4-Pillar Taxonomy)

### 1. `training`
Training execution, interval protocols, aerobic base, resistance & cross-training methodologies.
- **Topics**:
  - `Short_intervals` (e.g. 30s/15s, 40s/20s, SIT micro-intervals)
  - `Long_intervals` (e.g. 4x8min, 4x4min, 4x16min, sustained aerobic intervals)
  - `Decreasing_intervals` (Front-loaded / descending duration intervals)
  - `Fast_start_intervals` (Over-pacing early to accelerate VO2 kinetics)
  - `Progressive_overload` (Density, duration, and stimulus progression)
  - `Aerobic_base` (Low-intensity endurance training volume, Zone 2, polarized model)
  - `Sweet_spot` (Subthreshold aerobic density training, 88-94% FTP)
  - `Heavy_torque` (Low cadence / high torque cycling efforts, SFR, big gear force)
  - `Unilateral` (Single-leg vs bilateral resistance exercises)
  - `Sprint_performance` (Maximal neuromuscular power & rate of force development)
  - `Cross_training` (Modality transfer, run-to-bike transfer & multi-sport adaptations)
  - `Lab_vs_field` (Determining training zones/metrics in field vs metabolic cart)

### 2. `physiology`
Underlying biological mechanisms, cardiovascular remodeling, metabolic pathways, thresholds & markers.
- **Topics**:
  - `FTP` (Functional Threshold Power & threshold power modeling)
  - `CP` (Critical Power & power-duration hyperbolic curve)
  - `W_prime` (W' / Anaerobic Work Capacity & reconstitution)
  - `VO2max` (Maximum Oxygen Uptake & aerobic capacity kinetics)
  - `FatMax` (Maximal Fat Oxidation Rate & fat combustion zone)
  - `LT1_VT1` (First Lactate / Ventilatory Threshold, aerobic threshold, talk test)
  - `LT2_VT2` (Second Lactate / Ventilatory Threshold, MSS, MLSS, OBLA)
  - `Durability` (Fatigue Resistance over duration/kJ, late-ride power preservation)
  - `Power_vs_HR` (Intensity domain correlation, decoupling & cardiovascular drift)
  - `Heart_rate_variability` (HRV, rMSSD, autonomic nervous system, readiness)
  - `Cardiac_hypertrophy` (Eccentric left ventricular remodeling & stroke volume)
  - `Lactate_shuttle` (Monocarboxylate transporters MCT1/MCT4 & lactate clearance)
  - `Mitochondrial_density` (Mitochondrial biogenesis, PGC-1alpha & capillarization)
  - `Fat_oxidation` (Substrate utilization & glycogen sparing)
  - `Temperature_effects` (Heat stress, thermoregulation, sweat rate & core temp)

### 3. `nutrition`
Ergogenic aids, fueling strategies, hydration, buffering agents & energy balance.
- **Topics**:
  - `Carbohydrate_ratio` (Glucose to fructose 1:0.8 / 2:1 intake, g/hr & gut training)
  - `Sodium_bicarbonate` (Extracellular buffering agent & bicarb protocols)
  - `Beta_alanine` (Intracellular buffering agent / carnosine saturation)
  - `Hydration_electrolytes` (Fluid replacement, electrolyte balance & cramping prevention)
  - `Antioxidants` (Blunting vs aiding training adaptations, redox balance)
  - `Underfueling_REDs` (Relative Energy Deficiency in Sport / Low Energy Availability)
  - `Ergogenic_aids` (Caffeine, dietary nitrates/beetroot, creatine & supplements)

### 4. `planning`
Periodization models, workload distribution, microcycles, fatigue modeling & tapering.
- **Topics**:
  - `Block_periodization` (Focusing specific physiological stimuli into concentrated blocks)
  - `Double_threshold` (Norwegian subthreshold model / two sessions per day)
  - `Microcycles` (7-day, 10-day, shock microcycle designs & recovery scheduling)
  - `Tapering` (Pre-event taper protocols, volume reduction & peak readiness)
  - `TTA_TTE` (Time-to-Exhaustion modeling at FTP/CP)
  - `Volume_quantification` (TSS, work in zones, kilojoules, ATL/CTL/TSB load tracking)
  - `Periodization` (Macrocycle, mesocycle, annual planning & phase potentiation)

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
  - Long_intervals
  - Progressive_overload
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
