---
title: '60: Analysis and Use of Training Data'
language: en
category: training
topics:
  - Workload_quantification_and_modeling
  - Autonomic_and_cardiac_monitoring
  - FTP_and_functional_metrics
  - Durability_and_fatigue_mechanisms
  - Pacing_and_execution_dynamics
source: https://open.spotify.com/episode/6kJDVCiR3eAyhzmTKQ3d27
author: Daniele Bazzana, Stefano Nardelli
date: '2024-11-05'
summary: Explores real-time and post-hoc endurance cycling data analysis, distinguishing between external power metrics and internal physiological load, and evaluating power-duration profiles, decoupling, and training load modeling.
---

# 60: Analysis and Use of Training Data

## Overview and Physiological/Training Context

Modern endurance cycling produces an extraordinary volume of telemetry data through power meters, heart rate monitors, continuous glucose sensors, and muscle oxygenation devices. However, data acquisition is functionally useless without structured frameworks for interpretation. 

This episode explores how coaches and athletes should organize data analysis, establishing a clear hierarchy between **real-time on-bike metrics** (used to govern pacing, execute intervals, and monitor work) and **post-exercise analytical metrics** (used to evaluate physiological stress, track chronic adaptations, assess durability, and optimize recovery).

---

## 1. Real-Time vs. Post-Hoc Data Architecture

Effective data usage requires separating the live user interface on the bike computer from post-workout analytical software (e.g., TrainingPeaks, WKO5, Golden Cheetah).

### Real-Time Head Unit Configuration
Displaying too many metrics during high-intensity intervals or complex endurance rides creates cognitive overload and degrades execution quality. 
- **Interval Execution Screens:**
  - **Instantaneous 3-Second Smoothed Power (3s Power):** Dampens instant torque spikes while remaining responsive to rapid pedal acceleration.
  - **Lap Power & Lap Time:** Essential for pacing sustained threshold, VO2max, or tempo efforts without looking at total ride averages.
  - **Lap Cadence (RPM):** Critical for ensuring specific biomechanical and neuromuscular interval targets are met.
  - **Target Zone / Target Power Range:** Visual bounding box to prevent over-surging during the first third of an interval.
- **Endurance & Long Base Ride Screens:**
  - **Total Work (Kilojoules / kJ):** Fundamental for tracking total mechanical energy expenditure and planning intra-ride carbohydrate fueling (e.g., matching 60–90 g/h of carbohydrates against expenditure).
  - **Heart Rate (HR) and Power:HR Ratio:** Real-time indicator of cardiac drift and thermal/hydration strain.
  - **Time in Zones (TIZ):** Ensures the bulk of the session remains strictly within Zone 2 without excessive accidental excursions into Zone 3.

---

## 2. External Load vs. Internal Physiological Load

A fundamental principle of sports science is the distinction between what the athlete *does* mechanically and how the body *responds* biologically.

$$\text{External Load (Mechanical Work)} \iff \text{Internal Load (Physiological Strain)}$$

| Parameter Type | Primary Metrics | Physiological Meaning | Confounding Factors |
| :--- | :--- | :--- | :--- |
| **External Load** | Average Power (W), Normalized Power (NP), Work (kJ), W/kg | Mechanical power output generated at the crank/pedals | Calibration drift, drivetrain losses, gradient |
| **Internal Load** | Heart Rate (bpm), HRV, Blood Lactate, RPE, Core Temperature | Biological strain experienced by cardiovascular and metabolic systems | Heat, dehydration, caffeine, mental fatigue, glycogen depletion |

### The Power-to-Heart Rate Decoupling Index ($Pw:HR$)
Aerobic decoupling measures the divergence between external mechanical power and internal cardiovascular response over long steady-state bouts:
- **Calculation:** Compares the ratio of Normalized Power to Heart Rate in the first half of a steady endurance ride against the second half:
  $$Pw:HR\ \text{Decoupling (\%)} = \left( 1 - \frac{NP_2 / HR_2}{NP_1 / HR_1} \right) \times 100$$
- **Interpretation:**
  - **$< 3\% - 5\%$:** Excellent aerobic base and cardiovascular stability; minimal cardiac drift under current hydration/thermal conditions.
  - **$> 5\% - 8\%$:** Significant cardiovascular drift indicating peripheral fatigue, plasma volume contraction (dehydration), thermal stress, or insufficient low-intensity mitochondrial base for the given duration.

---

## 3. Advanced Post-Workout Diagnostics and Load Modeling

### Power-Duration (PD) Curve and Mean Maximal Power (MMP)
The Power-Duration curve maps the athlete's best historical power outputs across time durations from 1 second to several hours:
- **Short Neuromuscular Power (1s–15s):** Reflects ATP-PCr stores, maximal motor unit recruitment, and cadence/torque velocity profiles.
- **Anaerobic Capacity (30s–2min):** Reflects glycolytic rate and anaerobic work capacity ($W'$).
- **Maximal Aerobic Power / VO2max (3min–8min):** Identifies the physiological ceiling of aerobic power output.
- **Functional Threshold Power (FTP / 20min–60min):** Represents sustainable quasi-steady-state metabolic power.

### Quadrant Analysis (Force vs. Cadence Dynamics)
Quadrant analysis plots circumferential pedal force (Newtons) against pedal velocity (cadence) for every single pedal stroke:
- **Quadrant I (High Force, High Velocity):** Sprints, punchy climbs, anaerobic attacks.
- **Quadrant II (High Force, Low Velocity):** Steep gradients, low-cadence torque grinds (SFR), standing starts.
- **Quadrant III (Low Force, Low Velocity):** Easy recovery spinning, soft pedaling, drafting downhill.
- **Quadrant IV (Low Force, High Velocity):** High-speed flat cruising, spinning in the peloton.
- **Coaching Utility:** Identifies whether a rider achieves their target wattage via excessive muscle torque (muscular strain) or high cadence (cardiovascular strain).

### Longitudinal Load Quantification (PMC / TSS / CTL / ATL / TSB)
The Performance Management Chart tracks training stress accumulation based on the Banister impulse-response model:
- **Training Stress Score (TSS):** Quantifies volume and intensity:
  $$TSS = \frac{t \times NP \times IF}{FTP \times 3600} \times 100$$
- **Chronic Training Load (CTL / "Fitness"):** 42-day exponentially weighted rolling average of TSS.
- **Acute Training Load (ATL / "Fatigue"):** 7-day exponentially weighted rolling average of TSS.
- **Training Stress Balance (TSB / "Form"):** $TSB = CTL - ATL$.
- **Critical Pitfall:** TSS treats all stress identically; 100 TSS from a 2-hour Zone 2 ride produces vastly different neuromuscular and metabolic recovery demands than 100 TSS from 45 minutes of all-out anaerobic sprint intervals.

---

## Key Takeaways and Practical Recommendations

- **Keep Bike Computers Clean:** Display only actionable live metrics during workouts (3s power, lap power, lap time, cadence, target range) to maximize interval focus.
- **Monitor $Pw:HR$ Decoupling:** In endurance Zone 2 sessions, aim for aerobic decoupling under 5% across the targeted target race duration to confirm true aerobic durability.
- **Pair External with Internal Load:** Never evaluate mechanical power in isolation; always contextualize wattage against heart rate, perceived exertion (RPE), ambient temperature, and accumulated kilojoules.
- **Contextualize TSS:** Avoid chasing high CTL scores purely for volume; the physiological composition (intensity distribution) of the TSS is far more decisive for performance than the raw number.
