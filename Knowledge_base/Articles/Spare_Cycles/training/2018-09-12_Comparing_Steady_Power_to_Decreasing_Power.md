---
title: "Comparing Steady Power to Decreasing Power"
language: en
category: training
topics:
  - Short_intervals
  - VO2max
  - CP
  - Fast_start_intervals
source: "https://sparecycles.blog"
author: "Jem Arnold"
date: "2018-09-12"
summary: "Just a cool comparison from my workout yesterday, that offers a chance to compare steady-power 30/15s intervals to decreasing-power 30/15s intervals."
---

# Comparing Steady Power to Decreasing Power

Just a cool comparison from [my workout yesterday](https://www.strava.com/activities/1835002327), that offers a chance to compare steady-power 30/15s intervals to decreasing-power 30/15s intervals.

I set out to do 3x sets of [my favourite VO2max workout](https://sparecycles.blog/2017/12/13/prescribing-vo2max/), because with [the vascular issue in my leg](https://sparecycles.blog/2018/07/24/left-leg-burns/) ~~I’m scared of~~ I can’t do more effective [continuous power workouts](https://sparecycles.blog/2018/06/26/update-to-prescribing-vo2max/). I wasn’t sure what my power target should be, since I haven’t done any proper VO2max intervals for a few months. So I set targets conservatively based on my [current power-duration curve](https://sparecycles.blog/2017/10/26/2017-season-review-part-2/).

The workout targets were supposed to look like:

> [ 3×13 hard-start decreasing-power 30/15s… turned out to be waaay too easy. [https://sparecycles.blog/wp-content/uploads/2018/09/30-15_workout2_inked.jpg?w=1100](https://sparecycles.blog/wp-content/uploads/2018/09/30-15_workout2_inked.jpg?w=1100)  ](https://sparecycles.blog/wp-content/uploads/2018/09/30-15_workout2_inked.jpg)3×13 hard-start decreasing-power 30/15s… turned out to be waaay too easy.

### 

Immediately I could tell the power targets were too low, so as the intervals progressed I kept turning up the resistance to keep it hard. This unintentionally resulted in a fairly steady ~390-400 W power output for Set #1.

[ 30-15_WorkoutSets2_set1_Inked [https://sparecycles.blog/wp-content/uploads/2018/09/30-15_workoutsets2_set1_inked.jpg?w=1100](https://sparecycles.blog/wp-content/uploads/2018/09/30-15_workoutsets2_set1_inked.jpg?w=1100)  ](https://sparecycles.blog/wp-content/uploads/2018/09/30-15_workoutsets2_set1_inked.jpg)

### 

Let’s compare Set #1 to Set #2, where I started with the resistance ~10% higher and allowed the power to decrease through the set. The first hard-start interval was at ~425 W and the final interval was ~380 W.

[ Colours are automatic.. don’t blame me if they clash! [https://sparecycles.blog/wp-content/uploads/2018/09/30-15_workoutsets2_set2_inked.jpg?w=1100](https://sparecycles.blog/wp-content/uploads/2018/09/30-15_workoutsets2_set2_inked.jpg?w=1100)  ](https://sparecycles.blog/wp-content/uploads/2018/09/30-15_workoutsets2_set2_inked.jpg)Colours are automatic.. don’t blame me if they clash!

So what are we looking at?

  * First thing to notice are the power bars. Orange in the top chart (Set #1) and Yellow in the bottom (Set #2). This is raw second-by-second power.
  * In front of the power bars is a smoothed area of ‘MAP power’. Blue in Set #1, Purple in Set #2. This is a formula meant to estimate work done above 90% VO2max, using WKO4’s model for VO2max based on the power-duration curve.

ok, quick sidebar on ‘work’ and ‘workload’:

> ### What are ‘work’ and ‘workload’?
> 
> **Work** , in joules is the product of **power** (watts) multiplied by the **time** (seconds) that power was held.
> 
> Work (J) = Power (w ) * Time (s)
> 
> **Workload** , in kilojoules is then simply the cumulative work done for the given interval.
> 
> Workload (kJ) = sum( Power (w ) * Time (s) ) / 1000
> 
> **VO2max workload** represents the ‘raw’ power done through each set within the typical VO2max training zone, and is represented by the predominant orange and yellow power bars in the top and bottom charts, respectively
> 
> **MAP workload** estimates the work done above 90% VO2max, which is really the number that counts for a VO2max workout. Blue in the top chart, purple in the bottom.

The MAP expression tries to account for the slower ramp-up time of VO2 when each VO2max interval is initiated, so you can see by the coverage of each area over the power bars that not all of the VO2max workload is contributing to the MAP workload. The first part of each work interval is spent just ramping VO2 back up to 90%, before work can be accumulated above this target.

This is why the comparison between sets is so interesting!

> Compare Workloads for each set:
> 
> VO2max Workload  
>  Set #1: 159 kJ  
>  Set #2: 167 kJ
> 
> MAP Workload  
>  Set #1: 57 kJ  
>  Set #2: 101 kJ
> 
> While both VO2max workloads are within 5%, **MAP workload shows a massive ~43% difference!**

Normalized power was also higher in the second set (330 W vs 350 W) so maybe the improved quality of the second set is no big mystery, but I find the difference in MAP vs VO2max workloads the most interesting takeaway from this workout. This also suggests that NP is a better estimate of training workload than Avg power (which we kinda already know!)

Using intermittent intervals like the 30/15s and knowing the MAP formula, I could probably design a workout that would game it to maximize MAP workload, but the formula is just an approximation.

As a model, it’s sure to be wrong… [but it is useful](https://medium.com/@chasecottle/all-models-are-wrong-but-some-are-useful-c97d8f169a8e).

I’ll leave this with a sneak peak of a chart I’ve been working on that attempts to model VO2max training load using the MAP workload algorithm. It then tracks it in a PMC-like chart with Chronic and Acute training loads.

[ InkedVO2Workload_JA_Season2018 [https://sparecycles.blog/wp-content/uploads/2018/09/inkedvo2workload_ja_season2018.jpg?w=1100](https://sparecycles.blog/wp-content/uploads/2018/09/inkedvo2workload_ja_season2018.jpg?w=1100)  ](https://sparecycles.blog/wp-content/uploads/2018/09/inkedvo2workload_ja_season2018.jpg)
