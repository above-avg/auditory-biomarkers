# Acoustic cardiac variability research

Reproducible exploratory research on recorded heart sounds (PCG), ECG interval variability and post-exercise recovery. The proposed niche is participant-held-out, audio-only quality-based abstention for ultra-short acoustic cycle variability estimation.

## Deliverables

- `paper/ICIIPC2026_Heart_Sound_Variability.pdf` and `.docx`: 10-page conference manuscript in the official ICIIPC 2026 Springer template, with seven tables, five figures and twelve references. Authors supplied by the investigators: Pallab Sarangi, Shreyas Baloni and Pooja R Rao. Corresponding-author details and investigator approval remain outstanding.
- `paper/manuscript.md`: readable conference manuscript; `paper/manuscript_template.md` is its editable prose source. `paper/README.md` describes regeneration and submission limitations.
- `extended_analysis.py`: explicitly post-hoc rule comparisons, feature removal and alternative training-only coverage thresholds. Its primary predictions must exactly reproduce the original analysis.
- `manuscript.md`: empirical paper draft generated from measured results.
- `literature_review.md`: primary-source literature map, novelty boundaries and query log.
- `protocol.md`: analysis specification saved before cohort results, with engineering clarifications.
- `data/senssmarttech/`: complete open WFDB signal release, license, demographics, upstream hashes and verified manifest.
- `results/`: record and beat outputs, held-out predictions, participant fold audit, confidence intervals, comparisons, strata and figures.
- `analysis.py`, `download_data.py`, `test_analysis.py`, `audit_results.py`, `make_report.py`: reproducible workflow.

## Reproduce

Python 3.10 or newer. Dependencies are listed in `requirements.txt`; actual execution versions are saved in `environment.json`.

For exact dependency reproduction, install from `requirements-lock.txt`. `verification.log` records the synthetic/interface test run. `results/cohort_flow.csv` gives the inclusion decision and exclusion reason for each original record.

```powershell
python -m pip install -r requirements.txt
python download_data.py
python -m unittest -v test_analysis
python analysis.py
python audit_results.py
python make_report.py
python -m unittest -v test_extended_analysis
python extended_analysis.py
python paper/make_figures.py
```

Download uses the public `physionet-open` AWS mirror for SensSmartTech 1.0.0 and verifies each WFDB file against the release SHA256 manifest. No credentials are needed. Cached files are verified again. Signals occupy approximately 406 MB. Do not replace a versioned release without repeating provenance and analyses. A checksum failure stops execution.

## Scientific interpretation

This is a computational pilot and paper draft, not clinical validation. ECG beats and acoustic landmarks have not been expert-adjudicated. Audio-only events are acoustic cycle markers, not verified S1 labels. ECG-guided peaks are explicitly separated from standalone performance. Effective metric windows are approximately 26 seconds in nominal 30-second records. No frequency-domain HRV, disease diagnosis, blood pressure or physiological mechanism is established. The manuscript and literature audit explain what remains necessary for submission.

Data are licensed CC BY 4.0 by the original dataset authors. Cite the dataset and its accompanying paper; this project's scripts do not replace those credits. Source references appear in the literature review and manuscript. No paper has been submitted or findings published by this workflow.
