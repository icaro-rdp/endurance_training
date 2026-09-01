---
title: 'Watts Doc #21: VO2max and The Most Interesting Protein In The World — Complete Guide'
category: physiology
topics:
- VO2max_and_aerobic_kinetics
- Cardiovascular_and_hemodynamics
- Environmental_and_thermal_stress
source: Empirical Cycling Podcast — Kolie Moore & Kyle Harrison
author: Kolie Moore
date: '2020-07-03'
summary: An exploration of hemoglobin's allosteric cooperativity, the Bohr effect, pulmonary diffusion, and the relationship between plasma volume expansion, total hemoglobin mass, and the Frank-Starling mechanism.
key_takeaways:
- Hemoglobin's quaternary T-to-R state transition and sigmoidal binding curve enable rapid 98%+ saturation in lungs and efficient offloading in acidic, warm muscle tissue (Bohr effect).
- Hematocrit (concentration) does not predict VO2max (r ≈ 0.1); total hemoglobin mass and absolute blood volume are the true determinants (r ≈ 0.75).
- In the classic Coyle detraining study, re-infusing pure plasma restored 50% of lost VO2max by restoring stroke volume via the Frank-Starling mechanism, even as hematocrit dropped to 39.6%.
- Exercise-induced pseudoanemia (low hematocrit from rapid plasma volume expansion) is a beneficial endurance adaptation that lowers vascular resistance and enhances cardiac filling.
---

# Watts Doc #21: VO2max and The Most Interesting Protein In The World — Complete Guide
_Source: Empirical Cycling Podcast — Kolie Moore & Kyle Harrison_

---

## What Is Hemoglobin and the Oxygen Transport Cascade?

The oxygen distribution cascade links pulmonary ventilation, capillary diffusion, convective blood transport, and mitochondrial respiration. At the center of this cascade is **hemoglobin**, a tetrameric hemeprotein within red blood cells (erythrocytes) that reversibly binds molecular oxygen ($\text{O}_2$).

```
[Pulmonary Alveoli]   --->   [Hemoglobin Convective Transport]   --->   [Muscle Capillaries]
  50 m² Surface Area          - T-State (Low Affinity)                   - Bohr Shift Unloading
  Fractal Architecture        - R-State (High Affinity)                  - Myoglobin Diffusion
  200 mL Blood in Transit     - 4 O2 per Tetramer                        - Mitochondrial Sink
```

Rather than functioning as a passive carrier, hemoglobin exhibits sophisticated **allosteric cooperativity** and environmental sensing, modulating its binding affinity dynamically based on tissue $PO_2$, proton concentration ($\text{pH}$), carbon dioxide ($PCO_2$), 2,3-bisphosphoglycerate (2,3-BPG), and temperature.

---

## Key Physiological Mechanisms / How to Think About It

### 1. Pulmonary Gas Exchange & Fractal Alveolar Surface Area
* **Fractal Architecture:** The pulmonary tree branches across 23 generations, terminating in $\sim 300\text{ million}$ alveoli. This structural packing provides an immense **$50\text{ m}^2$ surface area** inside the human thorax.
* **Diffusion Efficiency:** Despite this massive surface area, only $\sim 200\text{ mL}$ of pulmonary capillary blood is present at any given millisecond. The alveolar-capillary membrane is ultrathin ($\sim 0.2\text{--}0.5\ \mu\text{m}$), allowing mixed venous blood ($PO_2 \sim 40\text{ torr}$) to fully equilibrate with alveolar gas ($PO_2 \sim 100\text{--}105\text{ torr}$) in $<0.25\text{ seconds}$.
* **Exhaled Oxygen Myth:** Exhaled air contains $\sim 16\%\ \text{O}_2$ not because the blood "refused" it, but because of anatomical dead space (trachea and bronchi) and normal ventilation-perfusion matching.

### 2. Hemoglobin Structure & Allosteric Cooperativity
Hemoglobin consists of four polypeptide globin chains ($\alpha_1\beta_1\alpha_2\beta_2$), each enclosing a planar **iron-protoporphyrin IX (heme)** group.
* **The Heme Subunit:** Ferrous iron ($\text{Fe}^{2+}$) forms six coordination bonds: four with pyrrole nitrogens of the porphyrin ring, a fifth with the proximal histidine residue (His F8), and a sixth reversibly binding $\text{O}_2$.
* **The Mechanical Snap (T to R Transition):**
  * **T-State (Tense / Deoxy):** In the unliganded state, the $\text{Fe}^{2+}$ atom sits $\sim 0.4\ \text{Å}$ out of the porphyrin plane in a domed shape.
  * **Oxygen Binding:** When $\text{O}_2$ binds, the iron atom shrinks electronically and moves $0.1\text{--}0.4\ \text{Å}$ directly into the porphyrin ring plane. This movement pulls the proximal histidine, transmitting a conformational torque across subunit salt bridges that snaps the entire tetramer into the **R-State (Relaxed / Oxy)**.
* **Sigmoidal Binding Kinetics:** This allosteric cooperativity produces an **S-shaped $\text{O}_2$-dissociation curve**. As each $\text{O}_2$ binds, the affinity of the remaining subunits increases up to 300-fold, ensuring near-$100\%$ loading in the lungs ($PO_2 > 90\text{ torr}$) while facilitating rapid, steep offloading as local tissue $PO_2$ drops below $40\text{ torr}$.

```
O2 Saturation (%)
100 |                 .-------- [Lungs: PO2 ~100 torr -> 98-99% Saturated]
 80 |              .-'
 60 |            .'    <--- Steep Unloading Phase in Muscle (PO2 20-40 torr)
 40 |          .'
 20 |       .-'
  0 +------+------+------+------+------> PO2 (torr)
    0     20     40     60     80   100
```

### 3. The Bohr Effect and Right-Shifting in Working Muscle
During high-intensity muscular work, local metabolic byproducts shift the oxygen-hemoglobin dissociation curve to the **right** (decreasing $\text{O}_2$ affinity, raising $P_{50}$ from $28\text{ to }40+\text{ torr}$):
1. **Acidity ($\text{pH} \downarrow$ / $\text{H}^+ \uparrow$):** Protons bind to specific histidine residues on deoxyhemoglobin, stabilizing the low-affinity T-state.
2. **Temperature ($\text{Temp} \uparrow$):** High muscular heat production ($>1100\text{ W}$) weakens $\text{O}_2\text{-heme}$ bonds, directly accelerating offloading.
3. **$\text{CO}_2$ Accumulation:** $\text{CO}_2$ reacts with terminal amino groups to form **carbaminohemoglobin** ($\sim 10\%$ of total $\text{CO}_2$ transport), releasing free $\text{H}^+$ and stabilizing the T-state.
4. **2,3-Bisphosphoglycerate (2,3-BPG):** Glycolytic intermediate in erythrocytes that nests in the central cavity of the T-state tetramer, preventing premature $\text{O}_2$ rebinding.

### 4. Carbonic Anhydrase Dynamics
Erythrocytes contain abundant **Carbonic Anhydrase**, a catalytically perfect enzyme that converts tissue $\text{CO}_2$ into soluble bicarbonate:
$$\text{CO}_2 + \text{H}_2\text{O} \xrightleftharpoons[\text{Carbonic Anhydrase}]{} \text{H}_2\text{CO}_3 \xrightleftharpoons{} \text{HCO}_3^- + \text{H}^+$$
* In working muscle, this reaction generates $\text{H}^+$ to fuel the Bohr effect.
* In pulmonary capillaries, the reaction instantaneously reverses, expelling $\text{CO}_2$ into the alveoli while consuming protons, left-shifting hemoglobin to maximize $\text{O}_2$ uptake.

---

## Practical Application & Prescriptions

### 1. Hematocrit vs. Total Hemoglobin Mass ($Hb_{\text{mass}}$)
* **The Concentration Fallacy:** Hematocrit measures the volume percentage of red cells in blood. In elite cohorts, hematocrit has **virtually no correlation with $\dot{\text{V}}\text{O}_2\text{max}$** ($r \approx 0.10$).
* **Total $Hb_{\text{mass}}$ and Blood Volume:** Absolute total hemoglobin mass ($\text{grams}$) and total blood volume ($\text{liters}$) correlate strongly with $\dot{\text{V}}\text{O}_2\text{max}$ ($r \approx 0.75$).

### 2. The Classic Coyle Detraining & Plasma Infusion Study
Coyle, Hemmert, and Coggan (1986) demonstrated the primacy of blood volume in cardiorespiratory performance:
* **Detraining (2–4 weeks couch rest):**
  * Total blood volume fell by **$9\%$** ($-350\text{ mL}$ plasma volume, $-130\text{ mL}$ RBC mass).
  * $\dot{\text{V}}\text{O}_2\text{max}$ dropped by **$6\%$** ($4.42\text{ to }4.16\text{ L/min}$).
  * Hematocrit paradoxically *increased* from $43.8\%\text{ to }45.7\%$ due to hemoconcentration.
* **Acute Plasma Re-infusion in Detrained Athletes:**
  * Re-infusing $350\text{--}400\text{ mL}$ of artificial plasma expander (Dextran/saline) with **zero red blood cells**:
  * Dropped hematocrit to a low $39.6\%$.
  * **Restored $50\%$ of the lost $\dot{\text{V}}\text{O}_2\text{max}$** ($4.16\text{ to }4.28\text{ L/min}$).
* **Mechanism:** Restoring plasma volume increased venous return, elevated End-Diastolic Volume (EDV), and restored **stroke volume ($SV$)** via the Frank-Starling law of the heart.

```
+-----------------------------------------------------------------------------+
|                     COYLE DETRAINING EXPERIMENT (1986)                      |
|                                                                             |
| Trained State         --> Blood Vol: 5.2 L | Hct: 43.8% | VO2max: 4.42 L/min|
| 2-4 Wk Detraining     --> Blood Vol: 4.7 L | Hct: 45.7% | VO2max: 4.16 L/min|
| + Plasma Reinfusion   --> Blood Vol: 5.1 L | Hct: 39.6% | VO2max: 4.28 L/min|
| (NO Red Cells Added!)                                                       |
|                                                                             |
| Conclusion: Stroke volume restored by Frank-Starling preload > hematocrit!  |
+-----------------------------------------------------------------------------+
```

### 3. Understanding "Exercise-Induced Pseudoanemia"
* When sedentary or deconditioned individuals start endurance training, plasma volume expands within **hours to days** via albumin retention and aldosterone/vasopressin upregulation.
* This dilutes the blood, dropping resting hematocrit (e.g., from 44% to 38%).
* **Performance Benefit:** Dilute blood lowers viscosity, reduces afterload on the left ventricle, enhances microvascular perfusion, and maximizes Frank-Starling cardiac preload.

---

## Common Pitfalls & Limitations

| Pitfall / Misconception | Physiological Reality | Practical Consequence |
| :--- | :--- | :--- |
| **"Higher hematocrit is always superior."** | Hematocrit above $\sim 50\%$ exponentially increases blood viscosity (Poiseuille's law), impairing cardiac filling, slowing capillary velocity, and risking thrombotic events. | Never chase isolated hematocrit numbers without assessing plasma volume and hydration. |
| **"Low hematocrit in athletes means clinical anemia."** | High plasma volume expansion dilutes red cells, causing beneficial 'sports pseudoanemia' while total $Hb_{\text{mass}}$ is elevated. | Check ferritin and total $Hb_{\text{mass}}$ before diagnosing iron deficiency in endurance athletes. |
| **"VO2 drops during workouts because blood runs out of O2 carrying space."** | At all times, pulmonary capillary transit fully oxygenates exiting arterial blood ($>98\%$ saturation). | Fatigue stems from peripheral metabolic stress and central hemodynamic strain, not pulmonary diffusion failure. |

---

## Summary Checklist / Decision Table

### Blood Volume & Hematology Diagnostic Matrix

- [ ] **Distinguish Concentration from Total Mass:** Never evaluate an athlete's aerobic capacity by hematocrit (%) or hemoglobin concentration ($\text{g/dL}$) alone; track total $Hb_{\text{mass}}$ via CO rebreathing or evaluate functional aerobic performance.
- [ ] **Value Plasma Volume Expansion:** Recognize that early endurance training gains and heat acclimation gains are driven by rapid hypervolemia enhancing left ventricular stroke volume.
- [ ] **Maintain Iron & Ferritin Reserves:** Ensure dietary iron availability so that slow erythrocyte synthesis ($Hb_{\text{mass}}$ expansion over weeks) can match fast plasma volume expansion.
- [ ] **Leverage the Bohr Effect:** Recognize that warm, active muscles and high cadence accelerate peripheral offloading from hemoglobin without requiring external interventions.
