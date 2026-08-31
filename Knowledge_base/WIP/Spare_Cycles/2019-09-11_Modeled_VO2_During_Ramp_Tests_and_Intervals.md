---
title: "Modeled VO2 During Ramp Tests and Intervals"
language: en
category: NaN
topics: NaN
source: "https://sparecycles.blog"
author: "Jem Arnold"
date: "2019-09-11"
summary: "We previously looked at how measured pulmonary VO2 (p VO2) compares to WKO-modeled VO2 (VO2 mod) during more-or-less constant work rate VO2max intervals. My conclusion was that modeling VO2 from power was unnecessary and would lead to less reliable and less valuable information than simply using power itself. This is mostly because VO2 mod is unabl"
---

# Modeled VO2 During Ramp Tests and Intervals

We previously looked at [how **measured pulmonary VO2 (_p_ VO2)** compares to **WKO-modeled VO2 (VO2 _mod_)**](https://sparecycles.blog/2019/07/17/vo2-measured-to-modeled/) during more-or-less constant work rate VO2max intervals. My conclusion was that modeling VO2 from power was unnecessary and would lead to less reliable and less valuable information than simply using power itself. This is mostly because **VO2 _mod_ is unable to capture the VO2 Slow Component** (VO2sc) and therefore **under-estimates _p_ VO2 during severe intensity workloads** above CP/FTP.

This limitation reflects an outdated assumption that VO2 for a constant workload can be modeled linearly from power during a ramp-incremental test. This is related to [an issue I’ve touched on before](https://sparecycles.blog/2017/11/22/the-problem-with-vo2max/). How ramp tests using different ramp rates will inevitably produce different results for ‘VO2max power’ (PVO2max) and estimates of Aerobic (AeT: LT1, VT1, etc.) & Anaerobic (AnT: LT2, VT2, MLSS, RCP, etc.) thresholds.

> [ Keir2018_Fig4 [https://sparecycles.blog/wp-content/uploads/2019/09/keir2018_fig4-1.jpg](https://sparecycles.blog/wp-content/uploads/2019/09/keir2018_fig4-1.jpg)  ](https://www.semanticscholar.org/paper/Using-ramp-incremental-V%CC%87O2-responses-for-exercise-Keir-Paterson/6507598a98ca33969385f3695688b6aae481e0f9/figure/3)
> 
> (top) Two ramp-incremental tests with different ramp rates showing VO2 vs Time, producing very different peak power outputs (POpeak, or PVO2max).
> 
> (bottom) VO2 vs Power for the same ramp tests as above, showing  
> similar LT1 (AeT) but very different RCP (AnT)
> 
> From [Keir et al, 2018 Fig 4](https://www.semanticscholar.org/paper/Using-ramp-incremental-V%CC%87O2-responses-for-exercise-Keir-Paterson/6507598a98ca33969385f3695688b6aae481e0f9)

This inconsistency between ramp test protocol is one persistent issue. Another is then translating the resulting workloads based on the ramp test results into prescription of constant work rate intervals. 

**Protocol Matters!** This is something I want to dig into another time. 

For now, the best way to understand the differences between ramp-incremental and constant work rate intervals, and the appropriateness of a linear VO2-power model in either context, is to see some real-world examples.

* * *

## VO2 During Ramp-Incremental Test

Recently I performed a series of maximal graded exercise tests to exhaustion under a few different protocol. The first was a traditional **incremental-ramp test** , where the workload was increased continuously at a ramp rate of 30 W/min until task failure.

Let’s look at how measured _p_ VO2 compares to modeled VO2 _mod_ for this typical incremental-ramp protocol.

> Ready for the transition from dark WKO4 charts to light WKO5 charts?
> 
> [ 30WminRamp11inked3 [https://sparecycles.blog/wp-content/uploads/2019/09/30wminramp11inked3.jpg](https://sparecycles.blog/wp-content/uploads/2019/09/30wminramp11inked3.jpg)  ](https://sparecycles.blog/wp-content/uploads/2019/09/30wminramp11inked3.jpg)
> 
> [Ramp-incremental test at 30 W/min](https://www.strava.com/activities/2618940789)  
> Pulmonary _p_ VO2 measured by _VO2 Master Pro_ and WKO-modeled VO2 _mod_
> 
>   * Power in yellow
>   * Blue line shows Right leg Power (good leg)
>   * Pink line shows Left leg Power (bad leg)
>   * Heart Rate in red, highlighted above 90% HRmax
>   * Modeled VO2 _mod_ in Dark Blue (in L/min) in the foreground, highlighted above 90% VO2 _mod_ max.
>   * Measured _p_ VO2 in Light Blue (in mL/min) in the background, highlighted above 90% _p_ VO2max
> 

> 
> Top Left Report:
> 
>   * Time >90% HRmax and >90% VO2max
>   * _p_ VO2peak is the peak 30sec _p_ VO2 achieved during this ramp test. This value (5270 mL/min) will be referenced as _p_ VO2max on subsequent charts, since this test is the most common ‘VO2max test’ protocol used in the literature.
>   * VO2 _mod_ peak is the peak 30sec VO2 _mod_ achieved during this ramp test. This value (5.150 L/min) will also be referenced as VO2 _mod_ max on subsequent charts. Importantly, I found this experimentally derived value to be more accurate than the historical estimate of VO2 _mod_ max (below)
>   * 90-day VO2 _mod_ max is the 90-day modeled VO2max, estimated from historical power data and the WKO power-duration curve. For whatever reason, possibly incomplete data informing the curve, this value is less accurate than the experimentally observed VO2 _mod_ max value (above)
>   * _R 2_ VO2 shows how closely the two VO2 lines are correlated
> 

Very close! On first glance clearly both VO2 lines are closely related, with a high _R 2_ coefficient. This is where modeled VO2 shines. [The algorithm used to infer VO2 _mod_](https://sparecycles.blog/2019/07/24/power-from-vo2-and-vo2-from-power/) from power would have been originally derived from a ramp-incremental test such as this.

Interestingly VO2 _mod_ possibly appears systematically lower than _p_ VO2 as intensity increases through the ramp. This could already reflect a subtle influence of VO2sc above Anaerobic Threshold that cannot be accounted for by the model. VO2peak values are very close at **5.170 L/min and 5270 mL/min** , respectively. The peak power output during this test was **443 W**. 

* * *

The second incremental-ramp test I performed was at a slightly higher ramp rate of 40 W/min until task failure. This ramp rate is far higher than would be typically performed. It was actually part of another experiment, but it provides a good comparison.

> [ 40WminRamp11inked3 [https://sparecycles.blog/wp-content/uploads/2019/09/40wminramp11inked3.jpg](https://sparecycles.blog/wp-content/uploads/2019/09/40wminramp11inked3.jpg)  ](https://sparecycles.blog/wp-content/uploads/2019/09/40wminramp11inked3.jpg)
> 
> [Ramp-incremental test at 30 W/min](https://www.strava.com/activities/2639446489)
> 
> Top Left Report:
> 
>   * Note that _p_ VO2max (5270 ml/min) and VO2 _mod_ max (5.170 L/min) are retained from the previous ramp test.
>   * Compare how closely both VO2peak values during this ramp test compare to previously.
>   * _R 2_ VO2 is virtually identical to previous.
> 

The ramp rates 30 W/min vs 40 W/min are close enough that the characteristics should be very similar for both tests. And indeed that is what we see. 30 W/min brought me to VO2max and task failure within 12min, while 40 W/min took only 9min. VO2peak values at failure were very close to each other and to previous VO2max values at **5210 mL/min and 5.230 L/min**.

The first inevitable difference with a steeper ramp rate and shorter test duration, is that I will be less affected by fatigue and peak power will be higher. For this 40 W/min ramp test my peak power output was quite a bit higher at **455W** at the end of ~9min compared to **443 W** at ~12min. This also explains the slightly higher VO2 _mod_ peak during this test.

We again see a possible slight under-estimation by VO2 _mod_ at higher intensities. This does seem to occur around my expected Anaerobic Threshold, suggesting it could be evidence of a VO2sc effect. However around the same intensity my [Left leg](https://sparecycles.blog/2018/07/24/left-leg-burns/) also begins to drop power to preserve tissue oxygenation (see the R/L power imbalance on the charts). So the systemic change in _p_ VO2-power may be exacerbated by this condition.

* * *

## VO2 During Step Test

What about constant work rate intervals with a much slower ramp rate? To get a better look at VO2 during constant workloads I performed a modified [5-1-5 assessment](http://my.moxymonitor.com/blog/how-to-complete-a-5-1-5-assessment). This is a novel incremental-step test designed by [Juerg Feldmann](https://youtu.be/Zk81bGYYZIQ) and the team at Moxy to be used with muscle oxygenation (SmO2) to assess physiological strengths and limiters across the intensity spectrum.

The 5-1-5 assessment consists of typically 5 load steps. Each load step is repeated for two 5min work intervals, with 1min passive rest (no pedaling) between each work interval. 

[ Screen Shot 2019-07-02 at 1.10.34 PM [https://sparecycles.blog/wp-content/uploads/2019/09/screen-shot-2019-07-02-at-1.10.34-pm.png](https://sparecycles.blog/wp-content/uploads/2019/09/screen-shot-2019-07-02-at-1.10.34-pm.png)  ](http://my.moxymonitor.com/blog/how-to-complete-a-5-1-5-assessment)

Example of a 5-1-5 assessment with load steps, [from Moxy](http://my.moxymonitor.com/blog/how-to-complete-a-5-1-5-assessment)

This test typically isn’t used to assess precise physiological thresholds or training zones, nor does it need to be performed to exhaustion and VO2max. But with some modifications **I think the 5-1-5 protocol can be adapted to assess thresholds and zones with better reliability and relevance to constant work rate intervals** _,_ than an incremental-ramp test.

> [ 5-1-5_11inked3 [https://sparecycles.blog/wp-content/uploads/2019/09/5-1-5_11inked3.jpg](https://sparecycles.blog/wp-content/uploads/2019/09/5-1-5_11inked3.jpg)  ](https://sparecycles.blog/wp-content/uploads/2019/09/5-1-5_11inked3.jpg)
> 
> [Modified 5-1-5 Incremental-step assessment at 50 W/step](https://www.strava.com/activities/2660205445)
> 
> Top Left Report:
> 
>   * Note the close match between _p_ VO2 and VO2 _mod_ at low intensities, as previously discussed. But as intensity increases during these longer intervals,  _p_ VO2 begins to outpace VO2 _mod_
>   * _p_ VO2peak reaches very close to the same _p_ VO2max as the previous ramp-incremental tests, however the model thinks VO2 _mod_ peak was nearly a full litre of oxygen consumption per minute _lower_ during this step test, because of the lower peak power achieved (355 W vs 430-440 W)
> 

Whereas the ramp-incremental tests brought me to exhaustion in 10-15min, the full 5-1-5 step test took just over an hour, clearly contributing to a lower end-test peak power. My peak power was **350 W** during the 5-1-5 assessment, compared to **445-455 W** peak power during the ramp-incremental tests. We’ll get back to the implications of these workloads in a moment.

Note that during the 2x5min work steps, _p_ VO2 began to outpace VO2 _mod_ as early as the third work step at 200 W. This is somewhere close to, but still I would expect under my Aerobic Threshold. Certainly the _p_ VO2-power relationship changes below Anaerobic Threshold, where the VO2 Slow Component (VO2sc) would be expected to affect the linear VO2-power relationship. 

I’ve seen this lower-than-expected non-linearity between _p_ VO2 and VO2 _mod_ with other athletes as well, so I don’t think this is cause by my particular blood flow limitation. Rather I suspect it reflects a true difference in _p_ VO2 reaching homeostasis during these 2x5min work steps at an elevated VO2 compared to what VO2 _mod_ would expect based on the ramp-incremental test.

* * *

##  Implications of Ramp Test VO2 vs Constant Work Rate VO2

Ramp-incremental tests are designed to elicit a linear relationship between workload (power) and physiological response (VO2, blood lactate, SmO2, etc.) in order to bring the athlete to task failure quickly enough such that VO2sc and other sources of fatigue have a negligible effect on that linear relationship. The idea is to be able to use that linear relationship to prescribe training intervals which are expected to elicit the same physiological response during constant work rate, as during the ramp test.

However this linear relationship clearly doesn’t hold for even modest 5-10 minute constant work rate intervals, as demonstrated in the 5-1-5 assessment. Nevermind for longer intervals around Anaerobic Threhsold where VO2sc would further exaggerate this difference.

The incremental-ramp test design basically elicits a constant [Phase II rise in VO2 kinetics](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5623047/). **The body’s physiological response is constantly trying to catch up to the increasing workload, without having time to reach homeostasis**. This design allows measurement of maximum VO2 well enough, but much of the information on changing internal states and metabolic efficiency (eg. physiological thresholds) along the way is lost.

I’ve argued about the importance of [understanding metabolic efficiency](https://sparecycles.blog/2019/07/17/vo2-measured-to-modeled/) across the intensity spectrum before, and the importance of internal measurements like Heart Rate, VO2, and SmO2. Knowing _how_ our body produces power, not just _how much_ power, **will let us optimize our training to target our particular physiological limiters, our goals, and to what our bodies can tolerate on any given day.**

* * *

## Prescribing Constant Work Rate VO2max Intervals

To conclude, let’s tie it all back to VO2max power and interval prescription.

For roughly the same VO2peak during all three tests (~5200 mL/min), my peak power varied from 350 W during the long duration 5-1-5 assessment, to 455 W during the fastest 40 W/min ramp test. That’s a massively different output for the “same” internal work!

Traditionally this peak power output might be prescribed as my target for VO2max intervals. But clearly the sustainable duration at these workloads will be drastically different. 455 W sounds horribly unsustainable, with or without a bad leg… 

Using the [estimated GE method of deriving aerobic contribution to power](https://sparecycles.blog/2019/07/24/power-from-vo2-and-vo2-from-power/) at **5270 mL/min _p_ VO2max**, at my estimated gross efficiency this equates to a range of **345-400 W** (yeah, there are some large error bars here). The 350 W achieved at the end of the 5-1-5 test is right in this range. So this might be a more appropriate target for maximizing volume >90% VO2max?

Which makes sense, since I was able to hold 350 W for a full 5min interval during that test. I failed during the second 5min 350 W step likely due to accumulated fatigue and only having a brief 1min recovery interval. I would expect to be able to perform around 4x5min intervals at 350 W with sufficient recovery intervals. ie. a classic VO2max interval workout. Whereas I know I wouldn’t be able to complete the same amount of time at 450+ W.

This sounds like something testable! I would be very interesting in seeing how much time >90% VO2max I can accumulate at 450 W and at 350 W, using constant work rate intervals. I only have so many high intensity workouts I can tolerate with my bad leg, but I should be able to do this experiment over the next few weeks. After I finish my current experiment comparing [VO2-guided](https://www.strava.com/activities/2694699772) and [SmO2-guided](https://www.strava.com/activities/2677491456) 30/15s microbursts.
