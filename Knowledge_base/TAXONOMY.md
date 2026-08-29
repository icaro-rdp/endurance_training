# Endurance Training Knowledge Base Taxonomy

This file is the canonical source for Knowledge Base categories, topics, and
source frontmatter. New Knowledge Sources must use only the exact topic values
listed here. Reviewed legacy exceptions are recorded in
[`docs/research/002-corpus-audit.md`](../docs/research/002-corpus-audit.md); they
must not be copied into new sources.

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
  - `Heart_rate_variability` (HRV / autonomic recovery tracking)

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
  - `Underfueling_REDs` (Relative Energy Deficiency in Sport / Low Energy Availability)
  - `Ergogenic_aids` (Supplements & performance enhancers)

### 6. `physiology`
Underlying biological mechanisms and environmental factors.
- **Topics**:
  - `Cardiac_hypertrophy` (Eccentric left ventricular remodeling & stroke volume)
  - `Lactate_shuttle` (Monocarboxylate transporters MCT1/MCT4)
  - `Temperature_effects` (Heat stress, thermoregulation & sex differences)
  - `Underfueling_REDs` (Endocrine, metabolic & physiological consequences of LEA)

### 7. `periodization`
Macrocycle, mesocycle, and microcycle planning and workload distribution.
- **Topics**:
  - `Block_periodization` (Focusing specific physiological stimuli into blocks)
  - `Double_threshold` (Norwegian subthreshold model / two sessions per day)
  - `Cross_training` (Modality transfer, cross-discipline substitution & multi-sport aerobic adaptations)
  - `Microcycles` (7-day, 10-day, shock microcycle designs)
  - `TTA_TTE` (Time-to-Exhaustion at FTP/CP)
  - `Volume_quantification` (TSS, Work in zones, Kilojoules)
  - `Heart_rate_variability` (HRV-guided training & recovery tracking)

---

## Canonical Frontmatter Contract

Every curated Markdown Knowledge Source must begin with a YAML mapping. The
current validator reports a blocking workflow error when any of these minimum
fields is missing or empty:

- `title`
- `category`
- `topics`
- `summary`

Every **new** Knowledge Source must use the fuller provenance contract below.
All shown fields are required for a new source; `key_takeaways` is the only
optional source field and belongs in frontmatter only when takeaways have been
deliberately curated from the evidence.

```yaml
---
title: "Document Title"
language: en
category: metrics
topics:
  - FTP
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
- `category` is exactly one of `metrics`, `hiit`, `zone2`, `strength`,
  `nutrition`, `physiology`, or `periodization`.
- Every topic uses the exact spelling and case from this file. Do not introduce
  a near-synonym as a one-off tag.
- `source`, `author`, and `date` record real provenance. A publication date uses
  `YYYY-MM-DD`; do not invent a date or provenance placeholder.
- `key_takeaways` is optional. Omit it when no takeaways have been deliberately
  curated; indexing does not synthesize it.

The passage layer derives `source_type`, repository-relative path,
`source_slug`, passage identifiers and boundaries, citation line ranges, and
size diagnostics. Those values do not belong in source frontmatter.

### Reviewed legacy compatibility

The existing corpus was reviewed as English before this contract was adopted.
A legacy source with no `language` field is therefore interpreted as `en`.
Explicit non-English metadata fails synchronization, and this compatibility
rule does not provide bilingual, translation, or language-detection support.
New sources still require `language: en`.
