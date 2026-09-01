---
title: 'Watts Doc #17: Why We Really Make Lactate — Complete Guide'
category: physiology
topics:
- Lactate_kinetics_and_metabolism
- Thresholds_and_metabolic_domains
source: Empirical Cycling Podcast — Kolie Moore & Kyle Harrison
author: Kolie Moore
date: '2020-04-07'
summary: An in-depth biochemical breakdown of why cells produce lactate, detailing enzyme kinetics (Michaelis-Menten, Km, Vmax), the essential role of LDH in regenerating NAD+ for glycolytic flux, and debunking hypoxia myths.
key_takeaways:
- Lactate is produced continuously in fully oxygenated cells at rest and during exercise, not because of oxygen deprivation (hypoxia).
- The Lactate Dehydrogenase (LDH) reaction strongly favors lactate formation (K_eq ~ 1.6 x 10^11), maintaining a resting 10:1 and exercise >500:1 lactate-to-pyruvate ratio.
- The primary evolutionary role of lactate formation is the instantaneous regeneration of cytoplasmic NAD+ from NADH to sustain glycolytic flux during rapid energy demand.
---

# Watts Doc #17: Why We Really Make Lactate — Complete Guide
_Source: Empirical Cycling Podcast — Kolie Moore & Kyle Harrison_

---

## What Is Lactate Production?

Lactate production is a fundamental, continuous biochemical process occurring in all human cells. Contrary to the enduring myth that lactate is a toxic, dead-end "waste product" born from oxygen starvation (hypoxia) and responsible for muscular fatigue, lactate is a high-energy, 3-carbon intermediary fuel and a necessary component of cytoplasmic redox balance.

At the conclusion of cytoplasmic glycolysis, a 6-carbon glucose molecule is cleaved into two 3-carbon molecules of pyruvate. In the cytosol, pyruvate has two primary pathways:
1. **Mitochondrial Transport & Oxidation:** Entry into the mitochondria via the mitochondrial pyruvate carrier (MPC) to be converted to Acetyl-CoA by Pyruvate Dehydrogenase (PDH) and metabolized in the Krebs cycle and oxidative phosphorylation.
2. **Reduction to Lactate:** Enzymatic conversion to lactate in the cytoplasm catalyzed by **Lactate Dehydrogenase (LDH)**.

Lactate formation is not an "emergency switch" that turns on when mitochondria fail; it is an active, near-equilibrium reaction operating at all times to maintain cellular homeostasis and rapid ATP production.

---

## Key Physiological Mechanisms / How to Think About It

### 1. Enzyme Kinetics & Catalysis Basics
Enzymes do not force impossible reactions; they are biological catalysts that lower the **activation energy barrier** ($\Delta G^\ddagger$) required for a spontaneous reaction to proceed through its precarious transition state.
* **Michaelis-Menten Kinetics:** Enzyme velocity ($V$) is governed by substrate concentration ($[S]$), maximal velocity ($V_{max}$), and the Michaelis constant ($K_m$).
* **$K_m$ and Affinity:** $K_m$ represents the substrate concentration at $50\% \ V_{max}$ and reflects substrate specificity/affinity. In human tissues, the $K_m$ of LDH for pyruvate is substantially lower than for lactate, meaning LDH has a significantly higher kinetic affinity for pyruvate in the cytosol.

```
       [Enzyme Active Site]
Pyruvate + NADH + H+ <===================> Lactate + NAD+
                         (LDH Catalysis)
```

### 2. The Directionality and Equilibrium of LDH
The conversion between pyruvate and lactate is catalyzed by Lactate Dehydrogenase:
$$\text{Pyruvate} + \text{NADH} + \text{H}^+ \xrightleftharpoons[\text{LDH}]{} \text{Lactate} + \text{NAD}^+$$

* **Massive Equilibrium Constant:** The equilibrium constant ($K_{eq}$) for the forward reduction of pyruvate to lactate is exceedingly high ($\sim 1.62 \times 10^{11}$). 
* **Equilibrium Ratios in Vivo:**
  * **At Rest:** The cellular ratio of lactate to pyruvate is approximately **10:1** ($\sim 1.0\text{ mM}$ lactate to $0.1\text{ mM}$ pyruvate).
  * **During Intense Exercise:** As glycolytic flux accelerates, the cellular lactate-to-pyruvate ratio swells to **500:1** or higher.
* Because LDH operates at near-equilibrium and exhibits high activity, any increase in cytosolic pyruvate concentration instantly drives a proportionate flux toward lactate formation. In the cytosol, this reaction flows overwhelmingly in the direction of lactate.

### 3. The Core Reason for Lactate: Instantaneous $\text{NAD}^+$ Regeneration
Glycolysis requires an uninterrupted supply of oxidized nicotinamide adenine dinucleotide ($\text{NAD}^+$) at the **Glyceraldehyde-3-phosphate Dehydrogenase (GAPDH)** step. In this reaction, $\text{NAD}^+$ is reduced to $\text{NADH} + \text{H}^+$.

* **The Cytosolic Bottleneck:** Cytosolic pools of free $\text{NAD}^+$ are extremely limited. Under high rates of ATP turnover (sprinting, hard accelerations, threshold efforts), cytosolic $\text{NAD}^+$ would be fully depleted within a fraction of a second.
* **Why Mitochondrial Shuttles Are Insufficient:** While mitochondrial shuttle mechanisms (e.g., the malate-aspartate and glycerol-phosphate shuttles) can transfer reducing equivalents into the electron transport chain, their transport rates are orders of magnitude too slow to keep pace with rapid glycolytic demand.
* **The Evolutionary Solution:** LDH immediately oxidizes $\text{NADH}$ back to $\text{NAD}^+$ right in the cytosol while converting pyruvate to lactate. This keeps cytosolic $\text{NAD}^+$ pools replenished, allowing GAPDH flux to continue and sustaining rapid anaerobic ATP generation. Without this mechanism, muscle contraction would abruptly halt during intense power spikes.

> [!NOTE]
> Producing lactate is an essential survival mechanism that uncouples fast cytosolic ATP production from the slower transport kinetics of mitochondrial shuttles.

### 4. Debunking the Hypoxia Myth
Lactate production is completely independent of intracellular oxygen deprivation:
* **Normal Intracellular $PO_2$:** In resting skeletal muscle, intracellular partial pressure of oxygen ($PO_2$) is $\sim 40\text{ torr}$.
* **Intense Exercise $PO_2$:** At $65\%\ \text{VO}_2\text{max}$ and above, intracellular $PO_2$ drops to $\sim 3\text{--}4\text{ torr}$.
* **Critical Mitochondrial $PO_2$:** The critical mitochondrial threshold required for maximal cytochrome c oxidase activity and oxidative phosphorylation is only $\sim 0.05\text{--}0.5\text{ torr}$.
* **Conclusion:** Even during maximal exercise, muscle tissue maintains intracellular $PO_2$ levels well above the critical mitochondrial limit. Mitochondria are fully oxygenated; lactate accumulates simply because glycolytic flux exceeds the catalytic capacity of pyruvate dehydrogenase (PDH) and mitochondrial respiration.

### 5. Glycolytic Nodes and Intermediary Branch Pathways
Glycolysis is not a rigid pipe; it functions as a connected series of equilibrium pools (analogous to a cascaded champagne fountain). Intermediates along the glycolytic cascade constantly supply essential branch pathways:
* **Pentose Phosphate Pathway:** Generates ribose-5-phosphate (for DNA/RNA synthesis) and $\text{NADPH}$ (for reductive biosynthesis and antioxidant defense).
* **Glycerol Synthesis:** Supplies glycerol-3-phosphate for triglyceride and phospholipid formation.
* **Amino Acid Synthesis:** Yields carbon skeletons for serine, glycine, and one-carbon metabolism.
* **Hexosamine Pathway:** Provides substrates for cellular protein glycosylation.

Maintaining steady glycolytic flux and dynamic pool equilibrium is therefore critical for broad cellular survival, not merely muscular contraction.

---

## Practical Application & Prescriptions

### 1. Understanding Glycolytic Flux vs. Aerobic Capacity
* **Lactate is Fuel, Not Waste:** Because lactate retains its 3-carbon backbone, it carries $>90\%$ of the chemical energy originally present in glucose. It is actively exported (via MCT4) and taken up by oxidative Type I muscle fibers, the heart, and the brain (via MCT1) to be oxidized.
* **Building the "Mitochondrial Sink":** Training should focus on expanding the aerobic sink—increasing mitochondrial density, capillarization, and MCT1 transporters in slow-twitch fibers—so that high rates of lactate production are matched by high rates of clearance and combustion.

### 2. Interpreting Blood Lactate Measurements in the Field
* **Static Blood Measurements are Net Balances:** Blood lactate concentration reflects the dynamic equilibrium:
  $$\text{Blood } [\text{Lactate}] = \text{Rate of Appearance } (R_a) - \text{Rate of Disappearance } (R_d)$$
* A low blood lactate value during a ramp test or steady effort does not automatically denote low glycolytic output; it may reflect exceptional clearance ($R_d$) by well-developed oxidative fibers.
* Conversely, high blood lactate accumulation can stem from an underdeveloped mitochondrial sink rather than an abnormally high anaerobic capacity.

---

## Common Pitfalls & Limitations

| Pitfall / Misconception | Physiological Reality | Practical Consequence |
| :--- | :--- | :--- |
| **"Lactic Acid" causes muscle burn.** | Lactate is an unprotonated base. The LDH reaction consumes a free proton ($\text{H}^+$), acting as an intracellular buffer. True acidosis is caused by non-mitochondrial ATP hydrolysis ($ATP \rightarrow ADP + P_i + H^+$). | Cease blaming lactate for fatigue; focus on managing peripheral fatigue from inorganic phosphate ($P_i$) and hydrogen accumulation. |
| **Lactate only appears under hypoxia.** | Intracellular $PO_2$ during heavy exercise remains far above the critical mitochondrial threshold ($3\text{--}4\text{ torr}$ vs $0.1\text{ torr}$). | Recognize that glycolytic rate, not lack of oxygen, drives lactate flux. |
| **"Flushing lactic acid" during recovery.** | Lactate is rapidly consumed by the heart and Type I fibers as a preferred aerobic substrate. | Active recovery does not "flush a toxin"; it maintains moderate blood flow and oxidative clearance of valuable fuel. |
| **Low lactate equals no glycolysis.** | Highly trained endurance athletes with massive mitochondrial density can combust lactate at rates near their production rate, masking high glycolytic flux. | Do not use isolated resting or submaximal blood lactate values as direct measures of glycolytic capability. |

---

## Summary Checklist / Decision Table

### Biochemical & Diagnostic Checklist

- [ ] **Acknowledge the Equilibrium:** Accept that lactate is always present in a 10:1 (rest) to 500:1 (exercise) ratio to pyruvate.
- [ ] **Recognize the Redox Driver:** Understand that lactate formation exists primarily to re-oxidize $\text{NADH}$ to $\text{NAD}^+$ for cytoplasmic glycolysis.
- [ ] **Differentiate Production from Clearance:** In physiological testing, analyze whether an athlete's threshold profile is limited by excessive glycolytic production ($VLA_{max}$) or deficient mitochondrial uptake and clearance ($R_d$).
- [ ] **Shift Focus to Aerobic Base:** Design training blocks (Zone 2 volume, long tempo, over-unders) that maximize mitochondrial enzymes and MCT1 expression to turn lactate into an aerobic performance asset.
