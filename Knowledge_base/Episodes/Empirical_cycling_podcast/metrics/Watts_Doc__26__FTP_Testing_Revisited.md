---
title: "FTP Testing Revisited: Power Curves, Critical Power, & Perceptual Ruts — Complete Guide"
category: "metrics"
topics:
  - "FTP"
  - "CP"
  - "TTA_TTE"
  - "Lab_vs_field"
source: "Empirical Cycling Podcast — Kolie Moore & Kyle Hanson (Watts Doc #26)"
author: "Kolie Moore"
date: "2020-09-14"
summary: "A deep revisit of FTP testing methodologies, examining the power-duration inflection point, mathematical vs. physiological limits of Critical Power (CP) models, how perceptual training ruts mask fitness gains, and robust field testing protocols."
key_takeaways:
  - "FTP is the distinct inflection point on the power-vs-log-time curve dividing slow, manageable aerobic fatigue from rapid, steep-sloped task failure."
  - "Critical Power (CP) mathematical models overestimate sustainable steady-state power (MLSS/FTP) by assuming infinite duration sustainability below CP."
  - "Athletes easily fall into 'perceptual ruts' when training extensively at a fixed wattage, anchoring their RPE to old numbers and masking genuine threshold improvements during open-ended tests."
  - "Power meter accuracy limits ($+/- 1–2%$) make single-watt FTP micromanagement unscientific; threshold operates within a functional 5–10 Watt physiological window."
  - "Continuous long, progressive open-ended tests (35–60+ min) and unstructured hard competitive efforts (Zwift races, KOMs) yield the highest-fidelity threshold data."
---

# FTP Testing Revisited: Power Curves, Critical Power, & Perceptual Ruts — Complete Guide
_Source: Empirical Cycling Podcast — Kolie Moore & Kyle Hanson (Watts Doc #26)_

---

## What Is Functional Threshold Power (FTP) Revisited?

Functional Threshold Power (FTP) is the field proxy for **Maximal Lactate Steady State (MLSS)**—the highest continuous work rate where blood lactate production is balanced by maximal lactate clearance.

Physiologically and graphically, FTP is identified as the **major inflection point on the power-vs.-log-time curve**:

```
                       Power-vs-Log-Time Inflection
  Power (W)
    ▲
    │   \ (Steep Slope: Severe Domain / Rapid W' Depletion)
    │    \
    │     \
    │      \───────────────┐ ◄── Inflection Point (True FTP / MLSS)
    │                      \
    │                       \ (Shallow Slope: Heavy/Moderate Domain / Glycogen Limited)
    │                        \
    └─────────────────────────────────────────► Log Time (Duration)
```

* **Above FTP (Severe Domain):** Small increases in power ($+5\%$) cause a non-linear collapse in time-to-exhaustion (TTE drops by ~50–75%) due to progressive $\dot{V}O_2$ slow component accumulation, rapid anaerobic reserve ($W'$) depletion, and intracellular acidosis.
* **Below FTP (Heavy/Moderate Domain):** Small decreases in power ($-5\%$) extend time-to-exhaustion dramatically ($+50\text{ to }+150\%$), as fatigue shifts from metabolic byproduct accumulation to substrate availability, thermoregulation, and peripheral neuromuscular strain.

---

## Key Physiological Mechanisms / How to Think About It

### 1. The Mathematical vs. Physiological Flaw in Critical Power (CP)
The classical Critical Power (CP) model fits work output to a 2-parameter hyperbolic equation:

$$P(t) = \frac{W'}{t} + CP$$

```
                   Critical Power Model vs. Reality
                   
  Power Output (W)
    ▲
    │   Hyperbolic Fit [Assumes CP sustainable indefinitely (t ──► ∞)]
    │   ──────────────────────────────────
    │   
    │   Actual Human Power Curve [Fails past 30-60 min due to glycogen & fatigue]
    │   ──────────────\
    │                  \─────────►
    └────────────────────────────────────────► Time (Duration)
```

* **The Infinite Duration Assumption:** The model assumes $CP$ is an asymptote that can be maintained indefinitely ($t \to \infty$) if glycogen were infinite. In reality, sustained heavy exercise incurs progressive neuromuscular fatigue, spinal inhibition, cardiac drift, and core temperature elevation.
* **The "Gray Zone":** Because CP is typically calculated from short trials (e.g., 3, 7, and 12 minutes), it heavily weights anaerobic capacity ($W'$) and neuromuscular recruitment. This results in CP values **15–30 Watts higher than true MLSS/FTP**, creating an unsustainable "gray zone" between heavy and severe domains.

### 2. The "Perceptual Rut" Phenomenon
When an athlete spends months performing intervals at a static assigned target (e.g., repeating $3 \times 20\text{ min}$ at 250 W):
* **Sensory Habituation:** The central nervous system establishes a hardwired sensory anchor (Rate of Perceived Exertion, RPE) to that specific power output and cadence.
* **Masked Adaptations:** If aerobic threshold improves by 15–20 W, the athlete will still gravitate to 250 W during an open-ended test because the familiar target feels "correct," while riding at their new 270 W threshold feels unnervingly foreign.
* **Breaking the Rut:** Athletes must occasionally be exposed to unstructured maximal efforts, Strava KOM attempts, uphill races, or blind time-boxed tests to expose true physiological gains.

```
                     Perceptual Rut Mechanism
                     
  [Static Submaximal Training (e.g. 250W for months)]
                        │
                        ▼
  [Sensory Habituation / RPE Anchoring]
                        │
                        ▼
  [Athlete Self-Selects 250W in Open Test despite +20W True Aerobic Gain]
```

### 3. Power Meter Physics and Single-Watt Fallacy
Commercial strain-gauge power meters feature manufacturer-calibrated tolerances of $\pm 1.0\%$ to $\pm 2.0\%$:
* For an athlete producing 300 W, an error margin of $\pm 1.5\%$ creates an inherent hardware variance of **$\pm 4.5\text{ W}$** (a 9 W total window).
* Daily biological variables (hydration status, glycogen fill, ambient temperature, sleep, caffeine) introduce another 2–4% flux.
* **Conclusion:** Micromanaging FTP to a single scalar integer (e.g., arguing 287 W vs. 289 W) is scientifically meaningless. Threshold must be treated as a **5–10 Watt operational zone**.

---

## Practical Application & Testing Protocols

### 1. Empirical Cycling Progressive Long Test Protocol
To eliminate anaerobic bias and accurately map the power-duration inflection point:

```
                  Progressive Open-Ended FTP Test
 ┌─────────────────┬───────────────────┬──────────────────────────────────┐
 │ Warm-Up         │ 15–20 min         │ Easy spinning + 2-3 brief openers│
 │ Phase 1 (Entry) │ 10–15 min         │ Target: ~15-20W below estimated  │
 │ Phase 2 (Ramp)  │ 15–20 min         │ Settle into target threshold     │
 │ Phase 3 (Max)   │ Open-ended (10m+) │ Ride to voluntary exhaustion     │
 └─────────────────┴───────────────────┴──────────────────────────────────┘
```

* **Phase 1 (10–15 min):** Start at 90–92% of estimated FTP. This prevents early anaerobic depletion ($W'$) and allows ventilatory and lactate kinetics to stabilize.
* **Phase 2 (15–20 min):** Gradually lift power to estimated threshold. Monitor ventilatory depth and muscle sensation.
* **Phase 3 (Open-Ended):** At minute 30–35, if legs feel strong, increase power by 5–10 W and ride until task failure.
* **Calculation:** Average power across the entire duration (typically 35–55+ min) represents true FTP and simultaneously defines current Time-to-Exhaustion (TTE).

### 2. Time-Boxed "Blind" Test (15–25 Minutes)
* **Application:** Used for athletes susceptible to pacing anxiety or stuck in perceptual ruts.
* **Protocol:** Instruct the athlete to execute a maximal 15-to-25 minute all-out effort without a fixed power ceiling.
* **Analysis:** Use the power data to populate multi-parameter power-duration models (e.g., WKO5 modeled FTP / mFTP) without the athlete attempting to hit a pre-conceived target number.

### 3. Testing Cadence and Frequency
* **Cadence Rules:** Ride at self-selected natural cadence (typically 85–95 RPM). Do not force artificial low or high cadence.
* **Testing Frequency:** Re-test every **8–12 weeks** or when power-duration model residuals show major upward drift. Mature athletes plateauing near their ceiling only need formal testing 2–3 times per season.

---

## Common Pitfalls & Limitations

```
                       FTP Testing Pitfalls
 ┌───────────────────────────────────┬───────────────────────────────────┐
 │ Common Error                      │ Physiological / Practical Consequence│
 ├───────────────────────────────────┼───────────────────────────────────┤
 │ Jumping straight to target power  │ Early acidosis; terminates test   │
 │ in the first 2 minutes            │ before true steady state reached  │
 ├───────────────────────────────────┼───────────────────────────────────┤
 │ Using Ramp Tests (Step Protocols) │ Overestimates FTP by 10-25% in    │
 │ to set threshold intervals        │ anaerobically gifted athletes     │
 ├───────────────────────────────────┼───────────────────────────────────┤
 │ Testing in Erg Mode               │ Removes sensory self-regulation;  │
 │                                   │ clamps cadence and induces spiral │
 ├───────────────────────────────────┼───────────────────────────────────┤
 │ Testing using Heart Rate targets  │ Cardiac drift, hydration, and heat│
 │                                   │ decouple HR from metabolic power  │
 └───────────────────────────────────┴───────────────────────────────────┘
```

1. **The Erg-Mode Testing Trap:** Executing FTP tests in Erg mode forces an artificial static resistance. If the rider fatigues slightly, cadence drops, torque spikes, and the trainer enters a "spiral of death." Always test in **Level/Slope/Resistance mode**.
2. **The "Vanity FTP" Downward Spiral:** Accepting an inflated FTP from a ramp test or 20-minute test without blowout causes future Sweet Spot and Threshold interval workouts to turn into supra-threshold anaerobic failure sessions.
3. **Heart Rate Misalignment:** Relying on a fixed threshold heart rate (e.g., 172 BPM) to determine power. Threshold heart rate shifts with plasma volume expansion, ambient temperature, fatigue state, and sympathetic tone.

---

## Summary Checklist / Decision Table

| Test Method | Accuracy for MLSS | Anaerobic Bias | Appropriate Use Case |
| :--- | :--- | :--- | :--- |
| **Long Progressive Test (35–60+ min)** | **Very High** | Minimal / None | Primary gold standard for true FTP & TTE determination. |
| **Time-Boxed Test (20–30 min all-out)** | **High** (when modeled) | Moderate | Populating power-duration models (mFTP) & breaking ruts. |
| **Hunter Allen 20-min Test (w/ Blowout)** | **Moderate** | Moderate | Field testing when continuous 40+ min roads are unavailable. |
| **20-min Test (Without Blowout)** | **Low / Poor** | High (5–12% error) | Punchy athletes will drastically overestimate FTP. |
| **Ramp Test (+25–30 W/min)** | **Very Poor** | Very High | Measures $\dot{V}O_2max$ / MAP, completely invalid for setting FTP. |
| **Critical Power 2-Parameter Model** | **Moderate / Low** | High at long $t$ | Predicts 3–15 min performance; overshoots continuous steady state. |
