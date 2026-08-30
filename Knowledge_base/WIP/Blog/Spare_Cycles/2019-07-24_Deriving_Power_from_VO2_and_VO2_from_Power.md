---
title: "Deriving Power from VO2 and VO2 from Power"
description: "The charts we looked at last week have some 'hidden' interesting features that I want to go into more detail on. This will get into mathematical derivations of metabolic equations, estimating Gross Efficiency, fuel utilization between fatty acids & glucose, and aerobic & anaerobic contribution to power output. This might get complicated, but it will…"
date: 2019-07-24
author: "Jem Arnold"
license: "CC-BY-4.0"
---

# Deriving Power from VO2 and VO2 from Power

<abstract lang="en">
The charts we looked at last week have some 'hidden' interesting features that I want to go into more detail on. This will get into mathematical derivations of metabolic equations, estimating Gross Efficiency, fuel utilization between fatty acids & glucose, and aerobic & anaerobic contribution to power output. This might get complicated, but it will…
</abstract>

The charts [we looked at last week](<https://sparecycles.blog/2019/07/17/vo2-measured-to-modeled/>) have some ‘hidden’ interesting features that I want to go into more detail on. This will get into mathematical derivations of metabolic equations, estimating Gross Efficiency, fuel utilization between fatty acids & glucose, and aerobic & anaerobic contribution to power output. 

This might get complicated, but it will serve as reference for many future discussions on modeling VO2 and anaerobic power.

> [ 3x5min1 [https://sparecycles.blog/wp-content/uploads/2019/07/3x5min1.jpg](https://sparecycles.blog/wp-content/uploads/2019/07/3x5min1.jpg)  ](<https://sparecycles.blog/wp-content/uploads/2019/07/3x5min1.jpg>)
> 
> 3x5min No Warm-up Intervals discussed last week
> 
>   * Power in yellow
>   * Heart Rate in red, highlighted above 90% HRmax
>   * Modeled VO2 in Dark Blue (VO2 in mL/min) in the foreground, highlighted above 90% Modeled VO2max
>   * Measured VO2 in Light Blue in the background, highlighted above 90% Measured VO2max
> 

* * *

## Deriving Modeled VO2 from Power

My conclusion last week was that **modeling VO2 from power alone is unfortunately too inconsistent and insufficient to provide additional value**. Despite this I still think it’s valuable to understand how VO2 is modeled from power to understand it’s limitations.

WKO models VO2 by looking at 25-second weighted rolling average power. This gives a more gradual slope to the VO2 curve, in approximation of VO2 kinetics. From that smoothed power a known metabolic equation is applied using the athlete’s weight and some constant values. I believe it’s based on the [ACSM formula for oxygen cost of cycling/leg ergometry](<https://sites.google.com/site/compendiumofphysicalactivities/help/unit-conversions>). 

> [ 3x5minModeled2 [https://sparecycles.blog/wp-content/uploads/2019/07/3x5minmodeled2.jpg](https://sparecycles.blog/wp-content/uploads/2019/07/3x5minmodeled2.jpg)  ](<https://sparecycles.blog/wp-content/uploads/2019/07/3x5minmodeled2.jpg>)
> 
> 3x5min no Warm-up Intervals  
> Raw and smoothed Power in yellow, and Modeled VO2 in dark blue
> 
> Note how the shape of the Modeled VO2 curve mirrors power. However the two lines are scaled to different y-axes. There is a method to the power-VO2 scaling. Keep reading!
> 
> WKO4_2019-07-16_09-44-42 [https://sparecycles.blog/wp-content/uploads/2019/07/wko4_2019-07-16_09-44-42.jpg](https://sparecycles.blog/wp-content/uploads/2019/07/wko4_2019-07-16_09-44-42.jpg) 
> 
> This formula converts Power in watts into estimated VO2 in L/min.

This conversion is simple enough. Especially since all the relevant calculations are built into WKO. For the reverse process of calculating power from VO2 I had to learn the conversion & formulae for myself.

* * *

##  Deriving Power from Measured VO2 

If we already have measured VO2 it’s actually a pretty simple calculation to derive power. However confirming all the math and the theory behind it took some time. The calculation starts with the known energy production of oxidizing glucose ([Péronnet & Massicotte, 1991](<https://www.ncbi.nlm.nih.gov/pubmed/1645211>)) and ends with the Gross Efficiency method of calculating aerobic contribution to power output ([Noordhof et al, 2011](<https://www.ncbi.nlm.nih.gov/pubmed/21563025>)). 

Let me start with the heavy math, then talk about the application. Feel free to skip this section unless you want to check my work!

###### 

> ## GE Method
> 
> A few methods exist for calculating power from VO2. The so-called ‘GE Method’ uses **Gross Efficiency** (GE) and either **Respiratory Quotient**(RQ) or **Respiratory Exchange Ratio**(RER; functionally the same thing) to calculate aerobic contribution to power output.
> 
> **RQ** or **RER** is the ratio of VCO2/VO2. **GE** is the experimentally derived difference between internal energy production and mechanical power output, accounting for losses as heat. Both of these values require measuring both VO2 and VCO2. This poses a problem since _VO2 Master Pro_ currently only measures O2 and not CO2. So we have to make some assumptions, which I’ll get into below.
> 
> GE Method, from [Noordhof et al, 2011](<https://www.ncbi.nlm.nih.gov/pubmed/21563025>)
> 
>   * Paer = PI * GE 
>     * where _Paer_ is aerobic contribution to mechanical power output (W )
>     * PI is metabolic power produced internally (W )
>     * GE is gross efficiency (%); the difference between PO (power output measured by the power meter) and PI.
>   * PI = VO2 * O2eq 
>     * VO2 is volume of O2 consumption in L/s 
>     * O2eq is energy equivalence of O2
> 

> 
> There are two slightly different constants given for O2eq. The first and more established equation is derived by [Garby & Astrup, 1987](<https://www.ncbi.nlm.nih.gov/pubmed/3577829>) from the nonprotein respiratory quotient table developed by [Lusk, 1924](<http://www.jbc.org/content/59/1/41.full.pdf>):
> 
> O2eq = 4940 * RER +16040 (arb. units)
> 
> However, apparently this table has been updated with slightly more precise values by [Péronnet & Massicotte, 1991](<https://www.ncbi.nlm.nih.gov/pubmed/1645211>). I see a mix of both constants used in contemporary literature… which is very confusing. I don’t know enough about the history here, or which table is commonly accepted. My inclination is to use the updated values, so this is what I will be using for the remainder of the article.
> 
> From [Péronnet & Massicotte, 1991](<https://www.ncbi.nlm.nih.gov/pubmed/1645211>), if we assume 100% glucose metabolism:
> 
> O2eq = 5.189 kcal/L = 21.7 kJ/L
> 
> This gives us a final formula for deriving aerobic power:
> 
> **Paer (W ) = VO2 (mL/min) * O2eq (kJ/L) * GE (%) * 1/60 (s) **

What’s the point of this conversion? The first idea was to be able to visualize VO2 and Power on the chart at the same y-axis scaling. Such that power output and VO2 ‘input’ would be displayed at the same point on the chart.

Briefly: at any power output, some portion of that power will be produced **aerobically** and **can be accounted for by VO2**. Under most conditions, some further portion of power will be produced **anaerobically** , **beyond what can be immediately accounted for by VO2**. (This is made up for by [excess post-exercise O2 consumption](<https://en.wikipedia.org/wiki/Excess_post-exercise_oxygen_consumption>), or O2 debt). If we can visually see how closely VO2 and power match at any given time, that should give us some information on how much of that power is being directly produced aerobically.

We can then infer that any gap between VO2 and power is either **coming from anaerobic sources** (visualized further below), or reflects a meaningful change in either **metabolic efficiency** (GE) and/or **fuel utilization** (fat or carb oxidation).

> [ 3x5minMeasured2 [https://sparecycles.blog/wp-content/uploads/2019/07/3x5minmeasured2-1.jpg](https://sparecycles.blog/wp-content/uploads/2019/07/3x5minmeasured2-1.jpg)  ](<https://sparecycles.blog/wp-content/uploads/2019/07/3x5minmeasured2-1.jpg>)
> 
> 3x5min no Warm-up Intervals  
> Power in yellow and Measured VO2 in light blue
> 
> Note near the end of the two ‘warm’ intervals (2 & 3) power and VO2 are approximately at the same point. This suggests close to 100% of the power produced at those points were being produced aerobically.
> 
> The first ‘cold’ interval shows a bigger gap between VO2 and Power. This probably reflects increased anaerobic contribution to power during this interval compared to the following intervals.
> 
> Note **PVO2max** (power at VO2max) reported under the VO2max dotted line. This is the power value calculated from the _Paer_ equation. **Very close to the power we see in reality when I was approaching VO2max**.

Because _VO2 Master Pro_ only analyses O2 without CO2, I cannot calculate either RQ or GE. So I have to make some significant assumptions to build a working power model from only VO2 measurement.

**The major assumption is that RQ is always equal to 1.00**. This gives us the predictable value for O2eq = 21.7 kJ/L for the _Paer_ equation (detailed above in the heavy math).

In reality RQ will change moment by moment with intensity and with factors such as fuel availability. RQ ranges from ~0.70 to ~1.00 for 100% fatty acid oxidation and 100% glucose oxidation, respectively. RQ tends to be lower (ie. greater relative fat burning) at lower intensities, and higher (ie. greater relative carb burning) at higher intensities. 

Fat_Glucose_Oxidation [https://sparecycles.blog/wp-content/uploads/2019/07/fat_glucose_oxidation.png](https://sparecycles.blog/wp-content/uploads/2019/07/fat_glucose_oxidation.png) 

Representation of fat & carb oxidation across intensity

**RQ is impossible to predict without direct measurement**. So this assumption will tend to **overestimate aerobic power** at most submaximal workloads. However the maximum difference is typically only 20-30 W. I think this assumption is an acceptable limitation until measuring RQ directly becomes feasible.

Given Assumption 1 we can solve for **Gross Efficiency** , which is the other unknown value in the _Paer_ equation. **[GE tends to be ~20%](<https://wattmatters.blog/home/2013/08/looking-under-hood.html>)**. From my experimentation applying the _Paer_ formula, the resultant estimated GE values for appropriate workouts seem to fall within a range of ~18-23%. This is in line with expectations.

Ultimately, the numbers that come out from this equation roughly make sense considering the stated assumptions and limitations. I’ve successfully been using the _Paer_ equation as an estimate for power at VO2 (PVO2) and the scaling keeps everything visually coherent in the charts.

* * *

## Aerobic & Anaerobic Power

The final big application of the VO2 to power conversion and the chart scaling is that I can display estimated ‘**anaerobic power** ‘ without any additional calculations. This is the **power produced beyond what VO2 can account for**. This won’t be a perfectly accurate number, for all the assumptions given above, but it gives us another visual reference point and lets us compare things like time and training load.

(edit: this looks similar to [a feature that was just introduced in WKO5](<https://www.wko5.com/training-impact-score>), which is probably implemented a heck of a lot more cleanly than my method. I’ll have to explore and report back!)

> [ 3x5minAN2 [https://sparecycles.blog/wp-content/uploads/2019/07/3x5minan2.jpg](https://sparecycles.blog/wp-content/uploads/2019/07/3x5minan2.jpg)  ](<https://sparecycles.blog/wp-content/uploads/2019/07/3x5minan2.jpg>)
> 
> 3x5min No Warm-up Intervals  
> Measured VO2 from  _VO2 Master Pro_ and Modeled VO2 from WKO4
> 
> Once again, I’m making a lot of assumptions on how VO2 converts to power, so take this as a _very rough_ estimate. It’s an imperfect model intended to represent how the two energy systems interact to meet power demand. Honestly, it could be argued this model is over-extrapolating the data just like the [VO2 model I discussed last week](<https://sparecycles.blog/2019/07/17/vo2-measured-to-modeled/>). But I think the additional information provided from this chart has added value to training prescription. Let’s just be aware of the application and the limitations.

At the onset of the work interval (especially the first ‘cold’ interval above) the aerobic system can’t produce enough instantaneous energy to meet the sudden power demand. Anaerobic energy production pathways are able to respond rapidly to meet this demand by consuming resources stored directly in the muscle. Meanwhile the aerobic system takes ~60-90 seconds to ramp up in the background to match supply to demand. Aerobic pathways then continue to work to recover some of the depleted anaerobic resources ([O2 debt](<https://en.wikipedia.org/wiki/Excess_post-exercise_oxygen_consumption>), mentioned above).

* * *

## Relative Workloads and Energy Contribution

Let’s finish by looking at the workloads for energy burned (kJ) by the aerobic system above 90% VO2max, and the anaerobic system for the 3x5min intervals.

WKO4_2019-07-22_15-30-56 [https://sparecycles.blog/wp-content/uploads/2019/07/wko4_2019-07-22_15-30-56-1.jpg](https://sparecycles.blog/wp-content/uploads/2019/07/wko4_2019-07-22_15-30-56-1.jpg) 

This report omits the recovery intervals

Time accumulation shows I spent _most_ of the 15min of “VO2max work” burning some anaerobic energy to produce the target 350 W. During the entire first ‘cold’ interval, and most of the subsequent two ‘warm’ intervals, I was producing at least some energy anaerobically while my aerobic system slowly ramped up to 90% VO2max.

However the workloads (in kJ) show how important aerobic energy contribution is to the target workload. Over 3x more energy came from aerobic pathways when I was above 90% VO2max, than the total energy from anaerobic pathways.

This is just a small example of how significant aerobic contribution is to power output at virtually all intensities. Even maximal 1min or 30sec efforts show a surprisingly large contribution from aerobic energy pathways, which is something we’ll look at in the future. Cycling is an endurance sport, first and foremost. **Our aerobic system is _by far_ the most important component of our fitness on the road**.

* * *

Next time I want to share some more interesting comparisons of measured & modeled VO2, with aerobic & anaerobic power contribution during intermittent high intensity intervals. And a _very cool_ look at real-time measured VO2 data from inside a Cat 1/2 Crit race! Keep an eye out for that.

<nav>
- Source: [Original Article](https://sparecycles.blog/2019/07/24/power-from-vo2-and-vo2-from-power/)
- Author: [Jem Arnold](https://sparecycles.blog/about/)
</nav>
