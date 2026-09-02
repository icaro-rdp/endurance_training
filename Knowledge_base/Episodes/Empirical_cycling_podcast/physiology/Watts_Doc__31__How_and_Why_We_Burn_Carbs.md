---
title: 'How and Why We Burn Carbohydrates: Glycolysis, Redox Balance, & Metabolic
  Flux — Complete Guide'
category: physiology
topics:
- Lactate_kinetics_and_metabolism
- Mitochondrial_and_cellular_adaptation
- Substrate_utilization_and_fat_oxidation
- Thresholds_and_metabolic_domains
- VO2max_and_aerobic_kinetics
- Cardiovascular_and_hemodynamics
- Biomechanics_fit_and_equipment
- Physiological_testing_and_diagnostics
source: 'Empirical Cycling Podcast — Kolie Moore & Kyle Hanson (Watts Doc #31)'
author: Kolie Moore
date: '2021-03-02'
summary: The document delves into the physiological mechanisms of glycolysis, lactate
  kinetics, and metabolic flux, highlighting the role of lactate as a redox sink and
  its importance in high-intensity exercise. It also discusses cardiovascular and
  hemodynamic adaptations, substrate utilization, and VO2max kinetics.
key_takeaways:
- Glycolysis is a 10-step cytosolic pathway that yields 2 ATP net from blood glucose
  and 3 ATP net from muscle glycogen, providing ATP at rates up to 100 times faster
  than mitochondrial fat oxidation.
- Phosphofructokinase-1 (PFK-1) acts as the primary committed rate-limiting gatekeeper
  of glycolysis, activated by rising AMP/ADP and inhibited by high ATP, citrate, and
  cellular acidosis.
- Cytosolic NAD+ availability is the absolute bottleneck for the Glyceraldehyde-3-Phosphate
  Dehydrogenase (GAPDH) step; without rapid NAD+ regeneration, glycolysis instantly
  halts.
- Lactate Dehydrogenase (LDH) functions as a vital cytosolic redox buffer, converting
  pyruvate and NADH into lactate and NAD+, allowing rapid anaerobic and aerobic glycolysis
  to proceed uninhibited.
- Carbohydrate oxidation is indispensable for high-intensity race-winning efforts
  (surges, VO2max intervals, sprints) because fat oxidation kinetics cannot meet sudden
  or heavy ATP turnover rates.
---
# How and Why We Burn Carbohydrates: Glycolysis, Redox Balance, & Metabolic Flux — Complete Guide
_Source: Empirical Cycling Podcast — Kolie Moore & Kyle Hanson (Watts Doc #31)_

---

## What Is Carbohydrate Metabolism in Exercise Bioenergetics?

Carbohydrates (stored as intracellular muscle and liver glycogen, or circulating as blood glucose) represent the body’s most versatile, high-powered substrate for ATP resynthesis. While human fat stores provide virtually limitless energy ($>50,000\text{ kcal}$), fat oxidation is kinetically constrained by multi-membrane transport, slow enzymatic turnover, and high oxygen cost per ATP generated.

In contrast, **glycolysis**—the 10-step cytosolic breakdown of 6-carbon glucose ($C_6H_{12}O_6$) into two 3-carbon molecules of pyruvate ($C_3H_4O_3$) or lactate ($C_3H_5O_3^-$)—can accelerate ATP generation by two orders of magnitude within milliseconds of increased energetic demand.

```
                      Overview of Carbohydrate Flux Pathways
                      
    [Muscle Glycogen] ──► Glucose-1-Phosphate (via Glycogen Phosphorylase)
           │                        │
           │                        ▼
    [Blood Glucose]  ──► Glucose-6-Phosphate (via Hexokinase, costs 1 ATP)
                                    │
                                    ▼  [PFK-1: Primary Rate-Limiting Gate]
                         Fructose-1,6-Bisphosphate
                                    │
                                    ▼  [Cleavage & Isomerization]
                         2x Glyceraldehyde-3-P (GAP)
                                    │
                       NAD+ ──► [GAPDH] ──► NADH + H+ (Requires NAD+!)
                                    │
                                    ▼  [Substrate-Level Phosphorylation]
                                 2x Pyruvate
                                ┌───┴───┐
                                │       │
                 [Mitochondrial Entry]  [LDH Reduction]
                        │                       │
                        ▼                       ▼
                   Acetyl-CoA            Lactate + NAD+
              (Krebs / ETC Oxidation)  (Regenerates NAD+ for GAPDH)
```

---

## Key Physiological Mechanisms / How to Think About It

### 1. The 10 Enzymatic Steps of Glycolysis

Glycolysis is divided into two distinct functional phases: the **Energy Investment Phase** (preparatory) and the **Energy Payoff Phase**.

```
                Phase 1: Energy Investment (Preparatory Phase)
 1. Glucose ─────────────────────────► Glucose-6-Phosphate (G6P)
    [Enzyme: Hexokinase]              (Costs 1 ATP; trapped in cell)
 2. G6P ─────────────────────────────► Fructose-6-Phosphate (F6P)
    [Enzyme: Phosphoglucose Isomerase]
 3. F6P ─────────────────────────────► Fructose-1,6-Bisphosphate (F1,6BP)
    [Enzyme: PFK-1]                   (Costs 1 ATP; ★ PRIMARY COMMITTED STEP ★)
 4. F1,6BP ──────────────────────────► Dihydroxyacetone-P (DHAP) + GAP
    [Enzyme: Aldolase]                (Cleaves 6-carbon sugar into two 3-carbon units)
 5. DHAP ◄──────────────────────────► Glyceraldehyde-3-Phosphate (GAP)
    [Enzyme: Triose Phosphate Isom.]  (Yields 2x GAP molecules per glucose)

                Phase 2: Energy Payoff Phase (x2 per glucose)
 6. GAP + Pi + NAD+ ─────────────────► 1,3-Bisphosphoglycerate + NADH + H+
    [Enzyme: GAPDH]                   (★ CRITICAL REDOX BOTTLENECK ★)
 7. 1,3-BPG + ADP ──────────────────► 3-Phosphoglycerate + ATP
    [Enzyme: Phosphoglycerate Kinase] (First substrate-level ATP generation)
 8. 3-PG ────────────────────────────► 2-Phosphoglycerate
    [Enzyme: Phosphoglycerate Mutase]
 9. 2-PG ────────────────────────────► Phosphoenolpyruvate (PEP) + H2O
    [Enzyme: Enolase]                 (Creates high-energy enol phosphate bond)
10. PEP + ADP ───────────────────────► Pyruvate + ATP
    [Enzyme: Pyruvate Kinase]         (Second substrate-level ATP generation)
```

#### Glycogenolysis vs. Exogenous Glucose Energetics
* **Exogenous Blood Glucose:** Requires phosphorylation by Hexokinase (step 1), consuming 1 ATP. Net yield = **2 ATP** per glucose molecule.
* **Intramuscular Glycogen:** Cleaved by **Glycogen Phosphorylase** directly into Glucose-1-Phosphate (G1P), which mutates to G6P without consuming ATP. Net yield = **3 ATP** per glucosyl unit.
* *Coaching Implication:* Well-stocked muscle glycogen is bioenergetically more efficient and yields ~33% more rapid anaerobic ATP than relying solely on systemic blood glucose.

---

### 2. Allosteric Regulation: The PFK-1 Master Switch

Phosphofructokinase-1 (PFK-1) controls the major rate of flux through glycolysis. It is allosterically regulated by the cellular energy charge:
* **Allosteric Activators (Energy Demand Signals):**
  * **AMP and ADP:** High turnover of ATP increases cellular AMP and ADP, binding allosteric sites on PFK-1 to dramatically increase its catalytic velocity ($V_{max}$).
  * **Fructose-2,6-Bisphosphate:** Potent feedforward activator.
  * **Inorganic Phosphate ($P_i$):** Generated from ATP hydrolysis, activates PFK-1.
* **Allosteric Inhibitors (Energy Abundance / Acidosis Signals):**
  * **ATP:** High resting ATP binds regulatory allosteric sites on PFK-1, lowering its affinity for F6P.
  * **Citrate:** Efflux of citrate from mitochondria signals an oversupplied Krebs cycle, turning down glycolytic flux.
  * **Protons ($H^+$ / Low pH):** Intracellular acidosis allosterically slows PFK-1 activity, serving as a protective brake against catastrophic cellular acidification.

---

### 3. The Redox Bottleneck: NAD+/NADH Equilibrium & GAPDH

Step 6 of glycolysis, catalyzed by **Glyceraldehyde-3-Phosphate Dehydrogenase (GAPDH)**, is strictly dependent on oxidized Nicotinamide Adenine Dinucleotide ($\text{NAD}^+$):

$$\text{GAP} + \text{P}_i + \text{NAD}^+ \xrightleftharpoons[\text{GAPDH}]{} 1,3\text{-BPG} + \text{NADH} + \text{H}^+$$

* The cytosolic pool of free $\text{NAD}^+$ is minute ($\sim 0.5–1.0\text{ mM}$).
* At high exercise intensities, glycolytic flux through GAPDH can deplete available cytosolic $\text{NAD}^+$ in a fraction of a second.
* **If $\text{NAD}^+$ is not immediately regenerated back from $\text{NADH}$, GAPDH arrests, halting glycolysis entirely.**

```
                     Cytosolic NAD+ Regeneration Mechanisms
                     
       [Mitochondrial Shuttles]                  [Lactate Dehydrogenase (LDH)]
  (Malate-Aspartate / Glycerol-Phosphate)         (Immediate Cytosolic Valve)
               │                                               │
               ▼                                               ▼
  - High mitochondrial dependency                 - Near-instantaneous equilibrium
  - Limited transport rate across IMM             - Pyruvate + NADH + H+ ◄► Lactate + NAD+
  - Constrained at high glycolytic flux           - Preserves high cytosolic [NAD+]
```

---

### 4. Why Lactate Is the Essential Hero, Not Waste

For decades, popular coaching lore claimed that lactate caused fatigue and represented an "anaerobic failure" of the cell. In biochemical reality:
1. **Lactate is an obligatory redox sink:** Lactate dehydrogenase (LDH) reduces pyruvate to lactate solely to regenerate $\text{NAD}^+$ for GAPDH:
$$\text{Pyruvate} + \text{NADH} + \text{H}^+ \xrightleftharpoons[\text{LDH}]{} \text{Lactate} + \text{NAD}^+$$
2. **Lactate consumes a proton:** The LDH reaction actually *buffers* cellular acidity by consuming one $H^+$ during pyruvate reduction.
3. **Lactate is energetic currency:** Lactate rapidly shuttles via Monocarboxylate Transporters (MCT1/MCT4) into adjacent oxidative fibers, the myocardium, or the liver (Cori cycle) where it is converted back to pyruvate and oxidized aerobically.

---

## Practical Application & Prescriptions

### 1. Fueling the Glycolytic Machinery in Training

Because high-intensity cycling performance (attacks, threshold TTs, VO2max intervals) is strictly dependent on high glycolytic throughput:

```
 Recommended Carbohydrate Intake Guidelines for Cyclists:
 ┌──────────────────────┬────────────────────────────┬────────────────────────────┐
 │ Session Intensity    │ Daily Carbohydrate Target  │ On-Bike Fueling Target     │
 ├──────────────────────┼────────────────────────────┼────────────────────────────┤
 │ Rest / Recovery Day  │ 3–5 g/kg body weight       │ Water / Electrolytes       │
 │ Low Intensity (Z2)   │ 5–7 g/kg body weight       │ 30–60 g/h (if >2 hours)    │
 │ Threshold / VO2max   │ 8–10 g/kg body weight      │ 60–90 g/h (1:0.8 Glu:Fru)  │
 │ Heavy Multi-Day/Race │ 10–12 g/kg body weight     │ 90–120 g/h (Trained gut)   │
 └──────────────────────┴────────────────────────────┴────────────────────────────┘
```

### 2. High Glycolytic Interval Protocols

To train glycolytic capacity, buffering, and rapid oxidative clearance:
* **Anaerobic Capacity / Glycolytic Power ($W'$ Replenishment):**
  * *Structure:* $5–6 \times 1\text{ minute}$ all-out at $130–150\%$ FTP with $4–5\text{ minutes}$ active recovery.
  * *Mechanism:* Drives maximal PFK-1 flux, massive lactate accumulation ($>12–16\text{ mM}$), and stresses MCT1/MCT4 transport and mitochondrial clearance mechanisms.
* **Over-Under Threshold Intervals:**
  * *Structure:* $3 \times 15\text{ minutes}$ alternating $2\text{ min at }105\%\text{ FTP}$ (high glycolytic flux / lactate accumulation) with $2\text{ min at }90\%\text{ FTP}$ (aerobic lactate clearance via Krebs cycle).

---

## Common Pitfalls & Limitations

1. **Viewing Carbs as "Dirty" or "Inferior" Fuel:** Attempting to force the body into burning only fat via severe carbohydrate restriction downregulates Pyruvate Dehydrogenase (PDH) and PFK-1, destroying threshold power and anaerobic capacity.
2. **Blaming Lactate for Fatigue:** Muscular fatigue during extreme glycolysis is caused by phosphate accumulation ($P_i$ inhibiting cross-bridge calcium binding) and ADP/AMP accumulation, not by lactate.
3. **Neglecting Glycogen Replenishment Timing:** Glycogen synthase activity peaks within 30–45 minutes post-exercise; delaying carbohydrate ingestion delays full glycolytic restoration for subsequent high-intensity training days.

---

## Summary Checklist / Decision Table

| Biochemical Element | Pathway Role | Regulatory Trigger | Practical Coaching Takeaway |
| :--- | :--- | :--- | :--- |
| **Hexokinase** | Phosphorylates blood glucose to G6P | Inhibited by product (G6P) | Consumes 1 ATP; exogenous glucose yields 2 ATP net. |
| **Glycogen Phosphorylase** | Cleaves muscle glycogen to G1P | Activated by AMP, Epinephrine, $Ca^{2+}$ | Bypasses Hexokinase; muscle glycogen yields 3 ATP net. |
| **PFK-1** | Converts F6P to F1,6BP | Activated by AMP/ADP; Inhibited by ATP/Citrate/pH | Main gatekeeper of glycolytic speed during surges. |
| **GAPDH** | Converts GAP to 1,3-BPG | Strictly requires oxidized $\text{NAD}^+$ | Primary enzymatic bottleneck during high-flux work. |
| **LDH Reaction** | Converts Pyruvate + NADH to Lactate + $\text{NAD}^+$ | Driven by mass action & cytosolic redox state | Regenerates $\text{NAD}^+$ to keep glycolysis functioning. |
| **MCT Transporters** | Shuttles lactate/protons across membranes | Upregulated by high-intensity base training | Allows oxidative fibers and heart to consume lactate as fuel. |
