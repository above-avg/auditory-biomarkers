# Participant Held Out Quality Gating for Ultra Short Heart Sound Variability Estimation

@authors

**Abstract.** Accurate average heart rate does not ensure accurate beat-to-beat variability from heart sounds. We evaluated an audio-only quality gate against an automated electrocardiographic comparator using SensSmartTech 1.0.0: 338 synchronized recordings from 32 participants before activity and during recovery. Of these, 316 passed comparator and feature checks. Acoustic events were extracted without ECG input. Six acoustic features predicted log absolute RMSSD disagreement through ridge regression and leave-one-participant-out evaluation; thresholds used training participants only. Participant-balanced heart-rate mean absolute error was 0.28 bpm, whereas RMSSD error was 15.33 ms. At a nominal 50% retention target, the gate accepted 159 recordings from 29 participants, with RMSSD error of 6.00 ms (95% participant-bootstrap interval 4.66-7.48). The paired selection effect was -9.36 ms (-14.32 to -5.32); matched random retention yielded 15.36 ms. Post-hoc periodicity and interval-variability rules gave errors of 11.67 and 8.23 ms at similar coverage. The results support reporting error alongside coverage. Short windows, automated reference timing and untested external transfer preclude clinical HRV equivalence claims.

**Keywords:** Phonocardiography, RMSSD, selective estimation, signal quality, participant validation.

## 1 Introduction

Heart sounds provide mechanical timing without electrical electrodes. Variability estimation depends on locating repeated events consistently. Multimodal studies show that agreement in mean heart rate can coexist with limited agreement in heart-rate variability (HRV) indices [1]. An acoustic system therefore needs to identify when an estimate should be withheld.

We evaluate this selective estimation decision on participants excluded from training, reporting retained-record error, recording and participant coverage, and a random-retention control. The experiment concerns ultra-short sensor agreement during rest and recovery. It does not test a disease biomarker or equivalence to conventional HRV.

<!-- page -->

## 2 Related Work and Study Data

### 2.1 Positioning within existing research

Quality assessment is established in phonocardiography (PCG). Springer et al. trained classifiers against expert quality labels [2], while Giordano et al. investigated signal-to-noise-based assessment [3]. Template matching has also been applied to heart-sound localization in forcecardiography [4]. These studies motivate quality-aware processing but address different targets from predicting absolute RMSSD disagreement. A recent SensSmartTech study compares average heart-rate estimation across sensing modalities [5]. Table 1 identifies the narrower question examined here without asserting first-ever novelty.

{{table_related}}

### 2.2 Dataset and analysis cohort

We used the complete, openly released SensSmartTech WFDB dataset, version 1.0.0 [6,7]. Recordings include synchronized ECG, PCG, photoplethysmography (PPG) and chest acceleration (ACC), resampled to a shared 1 kHz grid. Native sensor rates differ; resampling does not confer 1 ms timing accuracy. Dataset metadata identify before-activity and after-activity recordings. Table 2 gives the observed analysis flow. All downloaded signal and header files matched the upstream SHA256 manifest.

{{table_cohort}}

<!-- page -->

## 3 Signal Processing and Quality Features

### 3.1 Electrical comparator and acoustic events

ECG leads I and II were filtered at 5-25 Hz (third-order Butterworth, forward and backward), scaled to unit standard deviation, and independently processed with WFDB XQRS. Lead II supplied comparator times. Eligibility required cross-lead F1 at least 0.90 within 50 ms, at least 15 beats, and every interval between 0.30 and 1.50 s. Sequences excluded 0.5 s at each boundary. These checks cannot identify shared errors or establish normal-to-normal intervals.

PCG filtering used 25-150 Hz, followed by the absolute Hilbert transform and a 15 Hz envelope low-pass filter. Normalized envelope autocorrelation over lags of 333-1500 samples estimated a cycle period. A recurrence tracker selected candidate peaks within 0.65-1.35 estimated cycles of the preceding event. Its score combined log envelope height with a quadratic period-deviation penalty of weight eight. Missing candidates advanced the search by one cycle without creating a detected event. A peak-distance baseline required separation of 0.55 estimated cycles. Neither acoustic detector accessed ECG. Events are acoustic phase markers and are not verified S1 labels.

### 3.2 Interval metrics and gate inputs

For each modality, events in [2, 28) s defined the analysis window. At least ten intervals were required. For n intervals I in seconds, heart rate was 60 divided by their mean; interval SD used the sample standard deviation. RMSSD, in milliseconds, was defined as follows.

@rmssd_equation

Table 3 lists the six audio-only gate inputs. Features describe the complete extracted event sequence; metric computation uses the inner window. Short-window RMSSD agreement is distinct from validation against a five-minute reference [8,9].

{{table_features}}

<!-- page -->

## 4 Participant Held Out Evaluation

### 4.1 Training and inference

For each of 32 folds, one participant was held out in full. Standard scaling and ridge regression (alpha = 10) were fitted to the other participants. The target was log(1 + absolute acoustic-minus-ECG RMSSD error). Training weights gave each participant equal total weight; the scaler and threshold quantile were record-weighted. A median of training predictions defined the primary retention threshold. Held-out predictions at or below that threshold were accepted. ECG supplied training targets and evaluation comparisons, but no inference input (Fig. 1).

![Workflow](figures/fig1_workflow.png)
**Fig. 1.** Cohort flow and separation of training, inference and ECG-guided diagnostics. The gate is learned from other participants; all test scores use frozen fold parameters.

### 4.2 Estimands and uncertainty

Mean absolute error (MAE) was averaged within participants, then across participants. Percentile intervals used 2,000 participant bootstrap resamples (seed 20261013). Gate effects paired retained- and all-record means for participants with accepted data. A random-retention control sampled without replacement 1,000 times, matching accepted counts within each retained participant. Its simulation interval differs from the gate's bootstrap interval.

Bootstrap intervals condition on saved predictions and omit model-refitting uncertainty. Pooled difference plots are descriptive. Single-feature rules, feature-removal fits and 25%/75% training-quantile thresholds were added after primary inspection and are explicitly post-hoc.

<!-- page -->

## 5 Results

### 5.1 Detector and modality comparisons

All 338 records were processed without extraction failure. Twenty-two failed ECG comparator checks, leaving 316 records from all 32 participants. Median absolute difference between extracted mean ECG heart rate and metadata median-based heart rate was 0.34 bpm; the two definitions need not coincide.

{{table_methods}}

Acoustic recurrence gave a heart-rate MAE of 0.28 bpm but RMSSD MAE of 15.33 ms (Table 4). The simpler acoustic peak detector gave RMSSD MAE of 43.89 ms. This difference establishes sensitivity to the chosen detector within this experiment. PPG and ACC results come from simple fixed baselines and cannot rank the intrinsic accuracy of sensing technologies.

![Agreement](figures/fig2_agreement.png)
**Fig. 2.** Acoustic-minus-ECG differences against the mean of both measurements for (a) heart rate and (b) RMSSD. Each point is a recording. Colors and marker shapes identify the held-out gate decision. No inferential limits of agreement are asserted.

<!-- page -->

### 5.2 Primary retention result and participant coverage

The gate retained 159 of 316 eligible recordings (50.3%), or 47.0% of the source cohort. The paired comparison used 29 participants with accepted data; their all-record MAE was 15.36 ms. Table 5 separates the paired selection effect from the all-participant baseline.

{{table_gate}}

![Participant coverage](figures/fig3_participants.png)
**Fig. 3.** Retained and withheld record counts (a), with participant-level RMSSD errors (b). Participants 1, 10 and 21 had no retained record and therefore have no retained-error point. Lines connect the two means only where both exist.

Matched random retention yielded MAE 15.36 ms (central 95% simulation range 11.64-19.61); none matched the gate's lower MAE. The corrected fraction was 1/1001. Selection does not repair rejected measurements. Accepted-record errors still reached a 95th percentile of 18.95 ms and maximum of 51.32 ms.

<!-- page -->

### 5.3 Post Hoc Rule Comparisons and Feature Removal

Every additional rule used training participants to determine its threshold. Higher periodicity and lower interval coefficient of variation (CV) were treated as favorable. The full model had lower descriptive retained-set error than either rule at approximately 50% coverage (Table 6). Their retained participants differ, so these summaries do not establish a paired superiority claim.

{{table_ablation}}

![Operating points](figures/fig4_gates.png)
**Fig. 4.** Post-hoc operating points from training-only thresholds (a) and simpler rule comparisons (b). Error bars are conditional 95% participant-bootstrap intervals. Connected points summarize distinct selection policies, not a calibrated clinical risk curve.

Removing morphology or interval CV raised MAE to about 7.1 ms. Without spectral ratio, MAE was 5.95 ms across 30 participants; all six features are not demonstrably necessary. Observed coverage at the 25% and 75% targets was 25.6% and 75.6%, with MAE 5.01 and 8.90 ms across 23 and 30 participants. No clinically optimal threshold is established.

<!-- page -->

### 5.4 Filtering Sensitivity and Timing Diagnostics

The alternative acoustic bands gave broadly similar RMSSD errors (Table 7). ECG-guided peaks searched 15-160 ms after R for an S1 proxy, with 25-120 ms and 0-200 ms sensitivity windows. S2 proxies used 180-500 ms, truncated before the next beat. Guided events are conditioned on ECG and therefore belong to a separate diagnostic branch, not a deployable audio-only comparison.

{{table_sensitivity}}

![Event examples](figures/fig5_events.png)
**Fig. 5.** Five-second excerpts from the lowest and highest acoustic RMSSD-error recordings. Dots mark acoustic events and dashed lines mark automated ECG R events. The displayed envelope is normalized within each excerpt; errors use the complete analysis window. Selection is for error auditing, not population representation.

If an acoustic event Sᵢ occurs at Rᵢ + dᵢ, its interval differs from the electrical interval by dᵢ₊₁ - dᵢ. The implementation's matched-sequence identity residual was zero at stored precision. This verifies arithmetic consistency only. Observed delay includes physiological timing, filtering and localization error, which this experiment cannot separate.

Among 30 participants with before- and after-activity data, the after-minus-before MAE difference was 1.08 ms (95% interval -5.54 to 7.28), providing no evidence of a systematic exercise-related increase in error.

<!-- page -->

## 6 Discussion

The audio-only gate reduced retained-record disagreement on unseen participants, with substantial loss of coverage. A monitor that returns no value for some people cannot be characterized solely by successful-output accuracy. Source, eligible and participant-specific denominators make that limitation visible.

The random-retention control preserves participant composition and accepted counts. It does not remove all selection bias: accepted recordings may have lower physiological variability or easier acoustic morphology. Interval CV is related to estimated variability, so its predictive usefulness may partly reflect the endpoint's scale. The present data cannot distinguish these explanations causally.

Feature removal does not identify a uniquely necessary six-feature set. The benchmark needs comparison with stronger landmarks, including logistic-regression hidden semi-Markov segmentation [10], before attributing the tradeoff to a general property of acoustic monitoring.

### 6.1 Limitations and next validation steps

The effective window is approximately 26 s, and recovery can be nonstationary. Findings on ultra-short ECG recordings [8] do not establish equivalence for acoustic landmarks under this protocol. We make no spectral HRV, autonomic-state, disease-classification or blood-pressure claim. The cohort is small, uses one acquisition setup, and contains repeated measurements. No external test cohort or confirmatory preregistration was used.

ECG lacks expert beat adjudication, cross-lead agreement can miss shared mistakes, and acoustic phase is unlabeled. Future work should obtain blinded ECG and S1/S2 annotations, quantify annotator agreement, and repeat the endpoint analysis. Longer recordings such as EPHNOGRAM [11] offer a route to external validation, which has not been performed. Confidence intervals exclude model-refitting uncertainty; post-hoc feature comparisons require confirmation before selecting a final gate.

## 7 Conclusion

In this 32-participant exploratory benchmark, acoustic mean-heart-rate agreement was much stronger than RMSSD agreement. A participant-held-out quality gate retained 50.3% of eligible recordings with RMSSD MAE of 6.00 ms, compared with 15.33 ms across all eligible recordings. Its value is an explicit error-and-coverage tradeoff. Independent annotation, stronger detector baselines and external replication remain necessary before interpreting the approach as clinically reliable variability monitoring.

<!-- page -->

**Data and research transparency.** SensSmartTech [6] is available through PhysioNet [12] under CC BY 4.0. Original ethics approval is documented by the dataset authors; this secondary analysis asserts no local exemption. Code and results: https://github.com/above-avg/auditory-biomarkers. Primary revision: 7f8686f; post-hoc additions reproduce its predictions. The protocol was not publicly preregistered. The named authors remain responsible for verification and approval.

## References

{{references}}
