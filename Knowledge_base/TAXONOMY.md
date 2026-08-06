# Endurance Training Knowledge Base Taxonomy

This file defines the canonical taxonomy, categories, tags, and topic relationships for the Knowledge Base. All documents must reference topics listed in this file.

---

## Categories & Topics

### 1. `metrics`
Core physiological metrics, testing methodologies, and intensity domains.
- **Topics**:
  - `FTP` (Functional Threshold Power)
  - `CP` (Critical Power)
  - `W_prime` (W' / Anaerobic Work Capacity)
  - `VO2max` (Maximum Oxygen Uptake)
  - `FatMax` (Maximal Fat Oxidation Rate)
  - `LT1_VT1` (First Lactate / Ventilatory Threshold)
  - `LT2_VT2` (Second Lactate / Ventilatory Threshold / MSS)
  - `Durability` (Fatigue Resistance over duration/kJ)
  - `Power_vs_HR` (Intensity domain correlation & decoupling)

### 2. `hiit`
High-Intensity Interval Training protocols, mechanics, and session design.
- **Topics**:
  - `Short_intervals` (e.g. 30s/15s, 40s/20s)
  - `Long_intervals` (e.g. 4x8min, 4x4min, 4x16min)
  - `Decreasing_intervals` (Front-loaded / decreasing duration)
  - `Fast_start_intervals` (Over-pacing early to accelerate VO2 kinetics)
  - `Progressive_overload` (Density & intensity progression)

### 3. `zone2`
Sub-threshold aerobic base training and physiological adaptations.
- **Topics**:
  - `Aerobic_base` (Low-intensity endurance training volume)
  - `Fat_oxidation` (Substrate utilization & sparing glycogen)
  - `Mitochondrial_density` (Mitochondrial biogenesis & capillarization)
  - `Lab_vs_field` (Determining Zone 2 power/HR without metabolic cart)

### 4. `strength`
Resistance and strength training for endurance athletes.
- **Topics**:
  - `Heavy_torque` (Low cadence / high torque cycling efforts)
  - `Periodization` (Off-season vs in-season lifting)
  - `Unilateral` (Single-leg vs bilateral exercises)
  - `Sprint_performance` (Maximal neuromuscular power & rate of force development)

### 5. `nutrition`
Ergogenic aids, fueling strategies, and nutritional periodization.
- **Topics**:
  - `Sodium_bicarbonate` (Extracellular buffering agent)
  - `Beta_alanine` (Intracellular buffering agent / carnosine)
  - `Carbohydrate_ratio` (Glucose to fructose 1:0.8 / 2:1 intake)
  - `Antioxidants` (Blunting vs aiding training adaptations)

### 6. `physiology`
Underlying biological mechanisms and environmental factors.
- **Topics**:
  - `Cardiac_hypertrophy` (Eccentric left ventricular remodeling & stroke volume)
  - `Lactate_shuttle` (Monocarboxylate transporters MCT1/MCT4)
  - `Temperature_effects` (Heat stress, thermoregulation & sex differences)

### 7. `periodization`
Macrocycle, mesocycle, and microcycle planning and workload distribution.
- **Topics**:
  - `Block_periodization` (Focusing specific physiological stimuli into blocks)
  - `Double_threshold` (Norwegian subthreshold model / two sessions per day)
  - `Microcycles` (7-day, 10-day, shock microcycle designs)
  - `TTA_TTE` (Time-to-Exhaustion at FTP/CP)
  - `Volume_quantification` (TSS, Work in zones, Kilojoules)

---

## Schema Guidelines for Frontmatter

Every Markdown document in `Knowledge_base/` should contain YAML frontmatter adhering to this structure:

```yaml
---
title: "Document Title"
category: "metrics | hiit | zone2 | strength | nutrition | physiology | periodization | book"
topics:
  - "Topic 1"
  - "Topic 2"
source: "Origin URL, Podcast Name, or Book Title"
author: "Author / Speaker"
date: "YYYY-MM-DD"
summary: "1-2 sentence executive summary."
key_takeaways:
  - "Key point 1"
  - "Key point 2"
---
```
