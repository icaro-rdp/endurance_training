---
title: 'Fats vs. Carbs Part II: Carnitine Acetyl Buffering, CPT-1 Regulation, & VLamax Fallacies — Complete Guide'
category: physiology
topics:
- FTP_and_functional_metrics
- Substrate_utilization_and_fat_oxidation
- Sprint_and_anaerobic_intervals
source: 'Empirical Cycling Podcast — Kolie Moore & Kyle Hanson (Watts Doc #33)'
author: Kolie Moore
date: '2021-09-27'
summary: An advanced physiological and biochemical examination of how increasing exercise intensity suppresses fat oxidation through mitochondrial carnitine acetyl buffering, alongside a rigorous critique of the VLamax model and why glycolytic sprint capacity does not dictate Functional Threshold Power.
key_takeaways:
- 'Fat oxidation suppression during high-intensity exercise is caused by mitochondrial carnitine trapping: surging glycolytic flux converts free carnitine into acetylcarnitine to preserve the Coenzyme A pool for PDH, leaving insufficient free carnitine for CPT-1 fatty acid transport.'
- AMPK activation during exercise shuts down Acetyl-CoA Carboxylase (ACC), ensuring the resting Malonyl-CoA inhibition pathway is inactive during exercise; substrate competition for carnitine dominates instead.
- VLamax (maximal glycolytic rate) testing via short all-out sprints measures neuromuscular recruitment, total active muscle mass, and rapid ATP drawdown—not an intrinsic glycolytic 'leak' that undermines threshold power.
- Sprint power (Pmax) and Functional Threshold Power (FTP) operate as largely independent physiological dials; elite athletes can simultaneously possess a 2,000 W sprint and a 400 W+ FTP without one compromising the other.
- Substrate oxidation at FTP is highly individualized; well-trained endurance athletes can derive 30–50%+ of their energy from fat oxidation at MLSS, contradicting the VLamax theoretical assumption of 100% carbohydrate dependence at threshold.
---

# Fats vs. Carbs Part II: Carnitine Acetyl Buffering, CPT-1 Regulation, & VLamax Fallacies — Complete Guide
_Source: Empirical Cycling Podcast — Kolie Moore & Kyle Hanson (Watts Doc #33)_

---

## What Regulates Fuel Selection at High Intensity?

As exercise intensity escalates from low endurance base (Zone 2) through Functional Threshold Power (FTP) and into supra-threshold domains, whole-body substrate utilization shifts rapidly away from fat oxidation toward carbohydrate dominance. 

Historically, this transition was attributed either to allosteric enzyme inhibition or to an intrinsic "glycolytic strength" (popularized as **VLamax**) that supposedly overpowers aerobic metabolism.

In cellular reality, this shift is governed by an elegant mitochondrial emergency valve: **carnitine acetyl buffering**, which protects the cellular coenzyme A ($\text{CoASH}$) pool at the expense of long-chain fatty acid entry into the mitochondrial matrix.

```
                  The Mitochondrial Carnitine Acetyl-Buffering Valve
                  
  [High Glycolytic Flux / High Power Output]
                     │
                     ▼
          Pyruvate ──► [ Pyruvate Dehydrogenase (PDH) ]
                             │
                             ▼
              Accumulating Matrix Acetyl-CoA ──► Rapidly Depletes Matrix CoASH!
                             │
            ┌────────────────┴────────────────┐
            │                                 │
    (Without Buffering)               (Carnitine Buffering)
            │                                 │
     CoASH Exhausted                   [ CAT Enzyme ]
            │                  Acetyl-CoA + Free Carnitine ──► Acetylcarnitine + CoASH
     PDH Product-Inhibited                    │                                  │
            │                                 ▼                                  ▼
   Instant Cellular Arrest            Free Carnitine Pool                CoASH Pool Preserved!
   & Immediate Fatigue                 Is Depleted / Trapped              PDH Continues Running
                                              │
                                              ▼
                                 [ CPT-1 Fatty Acid Transport ]
                                 Deprived of Free Carnitine ──► Fat Oxidation Suppressed!
```

---

## Key Physiological Mechanisms / How to Think About It

### 1. The Coenzyme A Crisis & The Carnitine Solution

Coenzyme A ($\text{CoASH}$) is an indispensable cofactor for both carbohydrate oxidation (Pyruvate Dehydrogenase, PDH) and fatty acid $\beta$-oxidation. Because of its extremely high turnover rate, the intra-mitochondrial $\text{CoASH}$ pool is kept very small.

* **The Problem:** At high exercise intensities ($>80\text{--}90\%$ FTP), the rate of pyruvate influx from glycolysis exceeds the immediate turnover capacity of the Krebs cycle. Acetyl-CoA accumulates rapidly in the matrix. If left unchecked, all free $\text{CoASH}$ would be bound as Acetyl-CoA within $\sim 1\text{ second}$.
* **The Lethal Feedback:** Total depletion of free $\text{CoASH}$ triggers immediate, severe product inhibition of PDH, completely paralyzing carbohydrate oxidation and oxidative ATP synthesis.
* **The Carnitine Buffer:** To prevent cellular collapse, the enzyme **Carnitine Acetyltransferase (CAT)** transfers the acetyl group from Acetyl-CoA onto free L-carnitine, forming **acetylcarnitine** and regenerating free $\text{CoASH}$:

$$\text{Acetyl-CoA} + \text{Carnitine} \xrightleftharpoons[\text{CAT}]{} \text{Acetylcarnitine} + \text{CoASH}$$

* **The Trade-Off:** As free carnitine is sequestered into acetylcarnitine, the free carnitine pool available to **Carnitine Palmitoyltransferase-1 (CPT-1)** on the outer mitochondrial membrane plummets. Because CPT-1 requires free carnitine to shuttle long-chain acyl groups across the mitochondrial membrane, **fat oxidation is abruptly choked off**.

---

### 2. Rest vs. Exercise: Why Malonyl-CoA Is Inactive During Exercise

* **At Rest:** High carbohydrate ingestion stimulates insulin, activating Acetyl-CoA Carboxylase (ACC) to generate **malonyl-CoA**, which acts as a classical allosteric inhibitor of CPT-1 to halt fat oxidation while glycogen is synthesized.
* **During Exercise:** Muscle contractions dramatically increase AMP, activating **AMP-activated Protein Kinase (AMPK)**. AMPK directly phosphorylates and *inhibits* ACC, shutting down malonyl-CoA production.
* *Mechanism:* During exercise, fat suppression is **not** mediated by malonyl-CoA; it is strictly driven by the **carnitine substrate-trapping mechanism**.

---

### 3. Deconstructing the VLamax Model

The concept of **VLamax** ($\dot{V}La_{max}$—maximal glycolytic rate, measured in $\text{mmol}\cdot\text{L}^{-1}\cdot\text{s}^{-1}$ from a maximal sprint) originated in the 1980s (Mader & Heck). The mathematical model asserts that a "strong" glycolytic system (high VLamax) continually floods the cell with pyruvate and lactate at all exercise intensities, artificially suppressing FTP as a percentage of VO2max.

```
                     The VLamax Theoretical Claim vs. Reality
                     
    VLamax Theoretical Claim:
    [High Sprint Power / VLamax] ──► Floods Cells with Lactate ──► Lowers FTP % of VO2max
    
    Physiological Reality:
    [All-Out 15s Sprint] ──► Maximal Neural Drive ──► Recruits Fast-Twitch Motor Units
                                                                   │
                                                                   ▼
                                                       Instant Massive ATP Drop
                                                                   │
                                                                   ▼
                                                       Glycolysis Reactively Fills Demand
                                                       (Size Principle: Inactive at FTP!)
```

#### Core Flaws and Fallacies of the VLamax Framework:
1. **Reactive vs. Proactive Glycolysis:** Glycolysis does not push energy into the cell autonomously; it responds reactively to ATP breakdown products ($AMP, ADP, P_i$) generated by active myosin ATPases.
2. **Motor Unit Independence (Henneman's Size Principle):** A 15-second all-out sprint ($1,500\text{--}2,000\text{ W}$) recruits every available high-threshold Type IIx/IIa motor unit. At steady-state threshold ($300\text{--}400\text{ W}$), these extreme high-threshold fibers are not recruited. High sprint lactate production does not mean those fibers are producing lactate during submaximal riding.
3. **Independent Dials in Elite Athletes:** World-class sprinters (e.g., Marcel Kittel, André Greipel, Taylor Phinney) routinely exhibited both peak sprint powers $>1,800\text{--}2,000\text{ W}$ (massive VLamax) and sustainable FTPs $>400\text{--}450\text{ W}$ ($>80\text{--}85\%$ VO2max).
4. **Substrate Utilization at MLSS:** VLamax models assume substrate oxidation at FTP is 100% carbohydrate. Gas exchange (RER) data in well-trained endurance athletes demonstrate that fat oxidation can contribute $30\text{--}50\%+$ of total energy expenditure at Maximal Lactate Steady State (MLSS).
5. **Absence in Modern Exercise Physiology Literature:** Comprehensive mechanistic reviews by leading lactate authorities (e.g., George Brooks) do not attribute threshold kinetics to VLamax equations.

---

## Practical Application & Prescriptions

### 1. Training FTP vs. Sprint Ability: Stop Fearing Fast-Twitch Work

Athletes do not need to intentionally suppress their sprint capacity, avoid lifting heavy weights, or perform excessive low-cadence torque grinding out of fear of "raising VLamax."

```
 Empirical Cycling Framework for Threshold & Sprint Development:
 ┌──────────────────────┬────────────────────────────┬────────────────────────────┐
 │ Training Objective   │ Effective Stimulus         │ Target Adaptation          │
 ├──────────────────────┼────────────────────────────┼────────────────────────────┤
 │ Raise FTP (Aerobic)  │ High Volume + TTE Ext.     │ Mitochondrial mass, CPT-1  │
 │ Extend TTE @ FTP     │ 2x20min ──► 1x60min @ FTP  │ Krebs flux, capillary bed  │
 │ Sprint / Anaerobic   │ 5–15s Max Sprints + Lifting│ Neural drive, cross-bridge │
 │ Race Specificity     │ Over-Unders & Surges       │ MCT1/4 lactate clearance   │
 └──────────────────────┴────────────────────────────┴────────────────────────────┘
```

### 2. Pushing Out Time-to-Exhaustion (TTE) at FTP

To maximize mitochondrial density, capillarization, and fat oxidation capacity at threshold:
* **Progression Model:** Maintain power at $97\text{--}100\%$ FTP while systematically extending interval duration:
  * Week 1: $3 \times 15\text{ min}$ (45 min total work)
  * Week 2: $2 \times 25\text{ min}$ (50 min total work)
  * Week 3: $1 \times 50\text{ min}$ or $2 \times 30\text{ min}$ (50–60 min total work)
  * Week 4: $1 \times 60\text{--}70\text{ min}$ continuous threshold test/effort.

---

## Common Pitfalls & Limitations

1. **Trying to "Lower VLamax" with Artificial Constraints:** Avoiding sprints, heavy lifting, or high-intensity work to artificially lower lactate production blunts neuromuscular recruitment and top-end race fitness without providing any unique benefit to FTP.
2. **Assuming Low Sprint Power Equals High Aerobic Fitness:** A low sprint power often reflects poor neural recruitment, low total muscle mass, or chronic fatigue—not an inherently superior diesel threshold engine.
3. **Misinterpreting Post-Sprint Lactate Tests:** Athletes with exceptionally high aerobic fitness clear lactate so rapidly into working oxidative fibers that field blood lactate measurements taken 30–60 seconds post-sprint often significantly underestimate true peak lactate production.

---

## Summary Checklist / Decision Table

| Concept / Metric | Theoretical VLamax Model | Physiological Reality (Empirical Model) | Practical Coaching Action |
| :--- | :--- | :--- | :--- |
| **High-Intensity Fat Choke** | Allosteric inhibition / Glycolytic dominance | **Carnitine acetyl trapping** depletes free carnitine for CPT-1 | Accept carbohydrate necessity at $>85\%$ FTP; fuel accordingly. |
| **Pmax / Sprint Power** | Direct suppressor of FTP % VO2max | Independent neural/mechanical quality governed by motor unit recruitment | Train sprinting and heavy lifting freely for race-winning capacity. |
| **Substrate at Threshold** | Assumed 100% Carbohydrate | Variable ($50\text{--}100\%$ Carb, up to $50\%$ Fat) based on aerobic training status | Build mitochondrial mass via Zone 2 volume to raise fat use at FTP. |
| **Raising Threshold Power** | Suppress glycolysis / Low cadence grinds | **Progressive aerobic overload** (Zone 2 volume + long threshold TTE) | Progress threshold duration ($2\times 20 \to 1\times 60\text{ min}$) and overall volume. |
| **Lactate Dynamics** | Toxic byproduct driving early fatigue | Vital carbohydrate intermediate and mobile oxidative fuel | Train oxidative clearance via sustained threshold and over-under intervals. |
