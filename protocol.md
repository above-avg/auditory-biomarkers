# Analysis specification (written before signal results)

Date: 2026-10-13. This is a prospective analysis specification within this local project, not a public preregistration.

## Question and candidate contribution
Does audio-only quality-based abstention improve the agreement of ultra-short acoustic cycle variability with ECG interval variability during post-exercise recovery, when evaluation holds out entire participants? Compare mean heart-rate agreement with RMSSD agreement; use ECG-guided acoustic events only for an explicitly separate timing-error diagnostic. This combination is a candidate underexplored niche, not a verified first-ever contribution.

## Population and scope
Use the complete version 1.0.0 SensSmartTech WFDB release, all recordings and participants. Retain original before/after activity metadata. ECG is an algorithmic comparator without manually adjudicated normal beats, so describe ECG interval variability and acoustic cycle variability, rather than claiming clinically validated NN-HRV. Thirty seconds is not a validation against five-minute autonomic HRV. No LF/HF, disease classification, blood-pressure estimation or clinical thresholds are inferred.

Implementation clarification before extraction: metrics use event timestamps in [2,28) seconds within each nominal 30-second record to reduce boundary transients. The effective analysis is therefore approximately 26 seconds (or shorter when a record is shorter). Methods can still include different numbers of endpoint events. Random-retention controls match accepted counts within participants. Leave-one-subject-out folds and coefficients are saved for audit.

## Endpoints and validation
Primary: participant-balanced absolute RMSSD difference (ms), all eligible records versus an audio-only gate trained on other participants to target 50% retained coverage. Secondary: HR and SD interval differences, error by before/after activity and ECG HR bands, descriptive agreement plots, and record-level coverage. Use leave-one-subject-out (LOSO) fits and training-only scaling/thresholds. Subject cluster bootstrap (2,000 resamples, seed 20261013) gives uncertainty for subject-balanced means and paired gate effects. Report exclusions and failed/absent outputs, including subjects with no accepted record. The gate is exploratory and its threshold is not clinically calibrated.

## Baselines and diagnostics
Independent ECG QRS extraction from two leads, cross-lead agreement for comparator eligibility. PCG envelope autocorrelation estimates cycle period; a recurrence tracker chooses events without ECG access. A simpler peak-distance baseline measures sensitivity to the detector. PPG and ACC provide separate mechanical-sensor comparator baselines. ECG-guided S1/S2 windows provide an oracle diagnostic and exploratory R-to-acoustic-peak and acoustic systolic intervals; never mix these with audio-only performance.

Single-record engineering smoke check: unnormalized ECG failed the detector's amplitude assumptions. Before cohort extraction, ECG preprocessing was specified as zero-phase 5–25 Hz bandpass followed by unit standard-deviation scaling, then WFDB XQRS. Leads I and II are fixed; lead II gives reference timing, with lead-I event agreement checked at 50 ms. This is an engineering correction, not outcome-based parameter optimization.

The identity S1_i = R_i + d_i implies diff(S1) = RR + diff(d). RMSSD discrepancies can reflect delay variation and event-localization error. This algebra alone cannot distinguish physiology from measurement error. Sensitivity runs alter PCG frequency band and ECG-guided search windows. Synthetic timing tests check interval identity and leakage boundaries. Fixed methods are deliberately simple reproducible baselines; no state-of-the-art claims.

## Publication boundary
Complete the computational study and manuscript draft with real results, including negative results. A submission-quality claim still requires independent ECG/S1/S2 annotation, stronger segmentation baselines, external long-record replication (e.g. EPHNOGRAM), and an updated structured literature review. No guarantee of novelty, publication, clinical utility or causal mechanism.
