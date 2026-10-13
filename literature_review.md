# Literature map and novelty audit

Search date: 13 October 2026. Targeted web discovery and primary-source abstracts/full text where accessible; this is not a systematic review. Search-result dates were treated as unreliable. In particular, the forcecardiography paper is from 2024 even though a search result labeled it recent. No claim is made that the proposed niche has never been studied.

## Scope
“Auditory biomarker” is interpreted here as recorded cardiac acoustics (phonocardiography, PCG). This project does not study responses to audible stimuli or infer cardiac state from speech. PCG can be noninvasive while still requiring chest contact. ECG provides electrical beat timing; acoustic peaks are mechanical landmarks with physiological and instrumental delays.

## Closest primary sources

| Source | Established contribution | Consequence for this project |
|---|---|---|
| [Comparison of multiple cardiac signal acquisition technologies for HRV analysis (2019)](https://pubmed.ncbi.nlm.nih.gov/31463835/) | Compared several sensors against ECG around posture changes; average HR suitability did not ensure agreement for every variability index. | The HR-versus-HRV distinction is established, not our novelty. |
| [Li et al., variability of cardiac electromechanical delay (2019)](https://doi.org/10.1109/ACCESS.2019.2911555) | Studied delay variability in coronary disease and controls. Primary bibliographic record; full publisher text not retrieved in this audit. | Delay variability and disease application already exist. Do not propose their discovery. |
| [Automated signal quality assessment of mobile phone-recorded heart sounds (2016)](https://pubmed.ncbi.nlm.nih.gov/27659352/) | Tested heart sound recording quality assessment. | Signal-quality assessment alone is not novel. |
| [Automated assessment of phonocardiographic recording quality (2021)](https://www.mdpi.com/1424-8220/21/21/7246) | Examined noise and uncertainty in acoustic component localization. | Timing uncertainty is established; compare a gate with random selection and report event-detector dependence. |
| [Centracchio et al., accurate localization via template matching (2024)](https://doi.org/10.3390/s24051525) | ECG-free localization in forcecardiography, using manually selected templates in six resting subjects, including HRV comparisons. | A stronger segmentation comparator is needed before any performance superiority claim. |
| [EPHNOGRAM release (2021)](https://physionet.org/content/ephnogram/1.0.0/) | Synchronized ECG/PCG during rest and physical activity. | Long recordings support an independent replication cohort; their prior applications constrain electromechanical novelty. |
| [Electromechanical dynamics and exercise hysteresis (2024 preprint)](https://arxiv.org/abs/2410.19667) | Investigated exercise-related electrical/mechanical interval interactions. | Hysteresis alone is not a new gap. |
| [SensSmartTech release (2024)](https://physionet.org/content/senssmarttech/1.0.0/) and [dataset paper (2025)](https://doi.org/10.1038/s41597-025-05781-4) | Open synchronized ECG, PCG, PPG and acceleration before exercise and during recovery. | Appropriate paired data for rate-dependent measurement agreement; no disease endpoint. |
| [Heart Rate Estimation by Different Sensing Modalities (published 28 August 2026)](https://doi.org/10.1109/JSEN.2026.3726629) | Direct mean-HR comparison on SensSmartTech. | Simple multimodal HR benchmarking on this dataset is already published. Differentiate by variability and held-out quality gating. |
| [EarPCG (2026)](https://doi.org/10.1145/3774906.3800491) | In-ear sound recovery including beat-interval and SDNN evaluation. | Broader acoustic HRV feasibility and ear sensing are established. Our chest-PCG experiment cannot validate ear audio. |
| [Validity of (ultra-)short HRV recordings (2015)](https://pubmed.ncbi.nlm.nih.gov/26414314/) | Compared short ECG measures with longer references. | Duration validity is a distinct issue from simultaneous sensor agreement. |
| [Task Force HRV standards (1996)](https://www.escardio.org/static-file/Escardio/Guidelines/Scientific-Statements/guidelines-Heart-Rate-Variability-FT-1996.pdf) | Standard HRV measurement conventions. | Thirty-second recordings do not support general five-minute spectral HRV claims. |

Additional discovery: [Leakage-Aware Self-Supervised Cross-Modal Representation Learning](https://oiccpress.com/ijm2c/article/view/19009) describes PCG autonomic-state inference under LOSO. Its page has inconsistent date metadata (2025 citation, 2027 DOI, recent indexing). Exclude from chronologically firm claims until bibliographic details are resolved; nonetheless it prevents claiming LOSO alone as novel.

## Candidate niche

The plausible contribution is an **error-aware, participant-held-out benchmark of ultra-short acoustic cycle variability during post-exercise recovery**, testing whether an audio-only abstention rule selects recordings with lower RMSSD disagreement, alongside mean-HR agreement, random retention controls and detector/window sensitivity. The ECG-guided branch diagnoses how favorable beat localization changes the result. It is a study of measurement reliability, not a new disease biomarker or a new physiology claim.

This audit found adjacent work on every ingredient, but did not identify a directly equivalent combined study. Search absence is not proof of novelty. Before submission, search PubMed, IEEE Xplore, Scopus/Web of Science and citation chains of the closest 2026 study; record screening decisions and have a domain specialist assess overlap.

## Query log

Queries included: `PhysioNet simultaneous ECG PCG heart rate variability dataset`; `phonocardiogram heart rate variability electromechanical delay variability research`; `phonocardiogram HRV RMSSD signal quality selective prediction heart sound variability ECG agreement`; `"heart sounds" "RMSSD" "2026" Sensors`; `"phonocardiogram" "selective" "variability"`; `"SensSmartTech" "heart rate variability"`; `"Heart Rate Estimation by Different Sensing Modalities"`; `"Variability of Cardiac Electromechanical Delay" IEEE`; `"phonocardiogram" "RMSSD" "quality"`; `"heart sound" "variability" "abstention"`; `"SensSmartTech" "RMSSD"`; `"phonocardiogram" "HRV" "leave-one-subject"`.

Do not treat the query log as database-complete coverage, or search-engine snippets as verification of full methods. The downloadable signal release, source metadata, abstract statements, and full-text template-matching article were inspected directly where available.
