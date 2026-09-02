---
title: Investigating Power Asymmetry using Pedaling Metrics
language: en
category: training
topics:
- Torque_and_cadence_drills
- Threshold_intervals
- Pacing_and_execution_dynamics
- Zone2_and_endurance_base
- Biomechanics_fit_and_equipment
- Subthreshold_and_tempo
source: https://sparecycles.blog
author: Jem Arnold
date: '2018-07-05'
summary: The document comprehensively analyzes pedaling technique and power asymmetry
  through advanced metrics, focusing on torque, cadence, pacing, and biomechanics
  to enhance training and performance.
---
# Investigating Power Asymmetry using Pedaling Metrics

I’ve been using a [4iiii Precision Pro](https://4iiii-innovations.myshopify.com/collections/power-meters) dual-sided power meter for the past two seasons. Having a dual-sided power meter has been critical for me, as [I have a chronic injury](https://sparecycles.blog/2018/07/24/left-leg-burns/) which results in a significant Left/Right power asymmetry.

A single-sided power meter that just doubles Left leg power (my weak side) would give me unreliable data, not to mention I might never have realized I had such a severe imbalance at all.

4iiii recently enabled the advanced Garmin power metrics that allow for a more detailed investigation into pedaling technique and symmetry. I’ve spent the last few weeks learning how to interpret these metrics and drawing up some custom WKO4 charts.

Here’s what I’ve learned so far.

### 

> The ANT+ data channels are **Torque Effectiveness** and **Pedal Smoothness**.
> 
> **Torque Effectiveness** – How much of the total force (P+) + (P-) from each leg is contributing to forward momentum, as a percentage (P+ / (P+ + P-).
> 
> **Pedal Smoothness** – How evenly or spiky is the force applied through the 360° pedal stroke, as a percentage (Pavg / Pmax)
> 
> [ Imagestolen fromcourtesy of Garmin [https://sparecycles.blog/wp-content/uploads/2018/06/garminte.jpg?w=1100](https://sparecycles.blog/wp-content/uploads/2018/06/garminte.jpg?w=1100)  ](https://forums.garmin.com/forum/into-sports/cycling/vector/95966-cycling-dynamics-torque-effectiveness-te-and-pedal-smoothness-ps?p=691585#post691585)Image ~~stolen from~~ courtesy of Garmin
> 
> Normative values according to Garmin are 60-100% for Torque Effectiveness, and 10-40% for Pedal Smoothness. There’s no detail on how these numbers were arrived at, but the takeaway should simply be that there is a wide range of ‘acceptable’ values. [See Garmin’s introduction to the two metrics here](https://forums.garmin.com/forum/into-sports/cycling/vector/95966-cycling-dynamics-torque-effectiveness-te-and-pedal-smoothness-ps?p=691585#post691585).

The two metrics are difficult to interpret for everyday training without much context for what’s good or bad, or what target you should aim for. WKO4 has derived some important second order metrics that do a better job describing pedaling technique and give more actionable insight for training.

### 

### WKO4 Derived Pedaling Metrics

> **Gross Power Released (GPR)** – the downward power generated during the downstroke of each leg that is contributing to forward momentum, in Watts (P+)
> 
> GPR L ( W) = 1-leg Power L ( W) / Torque Effectiveness L (%)  
>  eg. GPR L = 100 / 80% = 125 W
> 
> **Gross Power Absorbed (GPA)** – the downward power generated during the upstroke of each leg that is  _resisting_ forward momentum, in Watts (P-)
> 
> GPA L ( W) = GPR L ( W) – 1-leg Power L ( W)  
>  eg. GPA L = 125 – 100 = 25 W
> 
> GPR and GPA are calculated independently for each leg.
> 
> (see pg. 6 from [WKO4 Pedaling Metrics ](https://irp-cdn.multiscreensite.com/dc479d29/files/uploaded/WKO4%20Pedaling%20Metrics.pdf)documentation for equations)

**Gross Power Released** comes primarily from your downstroke or power-phase as you actively generate force to pedal the bike forward (P+). There is also a smaller contribution from the release of inertial elastic potential energy stored within your tissues, however this contribution to GPR is less significant.

**Gross Power Absorbed** comes primarily from the upstroke as a result of any remaining downward force on the pedal as your leg returns to the top of the pedal stroke (P-). Your downstroke has to overcome these forces before any net remaining force can produce forward momentum of the bike.

These absorbed watts are caused by the force of gravity continuing to act downward on your leg as it lifts, as well as those same inertial forces that are now _storing_ elastic potential energy in your muscle tissues for the next downstroke. This has a more relevant contribution to GPA than GPR, since GPA is much smaller in magnitude.

Most of the literature on cycling biomechanics that I’ve encountered suggests that very few people actively push down through the upstroke. So most of the negative forces are passive rather than active.

For more information, Dr. Andy Coggan and WKO4 have published a [more in-depth discussion](https://irp-cdn.multiscreensite.com/dc479d29/files/uploaded/WKO4%20Pedaling%20Metrics.pdf) on the derivation of GPR and GPA.

> The net result of GPA and GPR is **Net Power Released (NPR)**_–_ the resultant power generating forward momentum during each leg’s downstroke.
> 
> Note, calculating NPR L/R will actually produce slightly different power numbers compared to L/R Power Balance. This is because power balance is reported directly from the power meter, and captures the total forces (P+ & P-) of each leg independently through the pedal stroke. While NPR reports the net positive power during each leg’s downstroke.
> 
> NPR for the _Left leg_ is the sum of _GPR Left_ and _GPA Right_. since while the Left leg is pushing down generating power, the Right leg is returning up absorbing some of that power.
> 
> Power ( W) = L leg power ( W) + R leg power ( W)  
>  eg. Power = 90 W + 110 = 200 W
> 
> NPR L ( W) = GPR L ( W) – GPA _R_ ( W)  
>  eg. NPR L = 125 – 35 = 90 W  
>  & NPR R = 135 – 25 = 110 W
> 
> NPR ( W) = (GPR L – GPA R) + (GPR R – GPA L)  
>  eg. NPR = (125 – 35) + (135 – 25) = 110 W
> 
> Don’t get too stuck on this for now. It will hopefully make more sense when we look at a real-world example later.

### 

### Dealing with a L/R Asymmetry

Unluckily for me, [I’m dealing with a chronic injury](https://sparecycles.blog/2018/07/24/left-leg-burns/) that has caused a significant L/R asymmetry for my entire cycling career (expect more details to come as I get closer to finding the cause of the issue).

My L leg begins to drop power as intensity goes up (and also gets really painful…) leaving my R leg to cover the difference. Luckily for you, I’ve put together some seriously cool charts to compare L/R Balance, GPR, and GPA of both legs!

Let’s take a look at a test I did on the turbo trainer the other day, designed specifically to elicit symptoms and demonstrate the power imbalance (don’t worry, I’m not causing any further damage to myself by doing this!).

First chart is a simple display of power, heart rate, and cadence.

[ 4iiii_Simple1 [https://sparecycles.blog/wp-content/uploads/2018/06/4iiii_simple1.jpg?w=1100](https://sparecycles.blog/wp-content/uploads/2018/06/4iiii_simple1.jpg?w=1100)  ](https://imgur.com/a/rdFMi2u)

  * Power in Yellow (FTP dashed yellow line, for context)
  * HR in Red (LTHR dashed red line)
  * Cadence in Green
  * The legend along the top shows the data points over the cursor, at time 23:42. The following charts will all show the cursor at this time point for comparison.

This Stress Test is my current [standardized warm-up](https://sparecycles.blog/2017/01/12/standardized-warm-up/) followed by a few [30/15 high-intensity intervals](https://sparecycles.blog/2017/12/13/prescribing-vo2max/), then a sustained hard threshold effort with spin-ups every ~45sec until failure.

### 

### L/R Power Balance

Let’s look at L/R balance for the stress test. This chart splits power into L and R legs independently, and shows L/R balance as it drifts away from 50/50.

[ 4iiii_Balance1 [https://sparecycles.blog/wp-content/uploads/2018/06/4iiii_balance1.jpg?w=1100](https://sparecycles.blog/wp-content/uploads/2018/06/4iiii_balance1.jpg?w=1100)  ](https://imgur.com/a/rdFMi2u)

  * Total Power in Yellow is shown in the legend for reference
  * Single leg FTP is shown (330 W / 2 = 165 W)
  * L leg power in Red
  * R leg power in Blue 
    * These numbers are what _each leg_ is doing _independently_
  * L/R Balance in White, smoothed to easily visualize and compared to 50/50
  * Average, min, and max L/R Balance for the workout are also given.

This chart visualizes where my L/R power balance begins to drift as I hit the high intensity intervals. For example, at the cursor (23:42) my power is 449 W. This is what I would see on my power meter at this moment. My L leg is contributing only 207 W, while my R leg is overcompensating at 242 W!

By the end of the stress test the red line (L leg power) and the blue line (R leg power) are mismatched by as much as 50 W!

### 

### Gross Power Released & Gross Power Absorbed

The following charts further split L & R power data into GPR L & R, and GPA L & R.

> Note, these charts are customized from stock WKO4 charts. Hunter Allen has [a good introduction to the pedaling metrics and charts on TrainingPeaks](https://www.trainingpeaks.com/blog/new-pedaling-charts-and-metrics-in-wko4/).

[ GPR_GPA1 [https://sparecycles.blog/wp-content/uploads/2018/07/gpr_gpa1.png?w=1100](https://sparecycles.blog/wp-content/uploads/2018/07/gpr_gpa1.png?w=1100)  ](https://imgur.com/a/rdFMi2u)

  * Gross Power Released (GPR) Left in pink
  * GPR Right in Green
  * Gross Power Absorbed (GPA) Left in orange
  * GPA Right in purple
  * White now shows smoothed  _GPR L/R balance_ with average, min, & max

Some interesting trends are visible: GPR L/R (how much power I’m pushing down with each leg through each downstroke) clearly contributes to the overall imbalance. But the asymmetry is less severe than L/R power balance by at least 1%.

So if GPR L/R explains  _most, but not all_ of the L/R power asymmetry where is the rest of the imbalance coming from?

Let’s take a look at the same chart, now showing GPA L/R balance in white. I’ve kept GPR L/R balance in darker grey to show the comparison.

[ GPR_GPA2 [https://sparecycles.blog/wp-content/uploads/2018/07/gpr_gpa2.png?w=1100](https://sparecycles.blog/wp-content/uploads/2018/07/gpr_gpa2.png?w=1100)  ](https://imgur.com/a/rdFMi2u)

  * GPR L & R, and GPA L & R same as above
  * GPA L/R balance in white, with average, min, & max
  * GPR L/R balance in grey

Right away we can see GPA L/R balance trends in the opposite direction to GPR L/R: **my L leg tends to absorb relatively more watts on the upstroke than my R** , especially as intensity increases through the stress test (GPA trends down). GPA L/R imbalance is also visibly more severe (relatively greater imbalance) than GPR L/R.

Considering GPR is significantly larger in magnitude than GPA, the combined imbalances of GPR and GPA explain the observed L/R power asymmetry.

> Net Power Released = NPR L + NPR R  
>  NPR = (GPR L – GPA R) + (GPR R – GPA L)  
>  449 W = (248 – 34) + (276 – 41)  
>  449 W = 214 W + 235 W
> 
> Recall that L/R power balance will show slightly different numbers to NPR L/R due to capturing the total power from one leg through the pedal stroke, vs the net power from both legs for each downstroke.
> 
> Power = L leg power + R leg power  
>  Power = (GPR L – GPA L) + (GPR R – GPA R)  
>  449 W = (248 – 41) + (276 – 34)  
>  449 W = 207 W + 242 W
> 
> There’s our original numbers! L/R power balance = 46/54

### 

### Conclusion & Further Questions

Looking in-depth at GPR and GPA suggests that not only is my L leg **pushing down with less force** than my R leg on the downstroke (lower GPR), but it also **resists being lifted with more force** than my R leg on the upstroke (higher GPA).

So my R leg literally has to drag along my L leg as I work above threshold!

I find this fascinating… I have to think more about why this is happening. It could be biomechanical (how my muscles are firing) or neuromechanical (how my brain is signaling the muscles to fire) or an issue with tissue composition (how elastic or fibrotic are my muscles, tendons, & fascia)… or something else completely (I’m open to ideas!)

It will be interesting to investigate this L/R asymmetry further under different conditions: such as longer intervals at various workloads, or how it responds in a race. In terms of why I have this asymmetry in the first place, I’m in the process of investigating and I will hopefully have some answers soon…

Keep an eye on the blog for more!
