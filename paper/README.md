# ICIIPC 2026 manuscript

The PDF and editable Word manuscript use the official Springer sample linked by
[ICIIPC 2026](https://iciipc.co.in/papersubmission.html), retrieved 13 October 2026.
They contain 10 pages, seven tables, five figures and twelve references.
The conference site specifies 6-10 pages including references. The home page
currently lists a 20 October 2026 submission deadline, superseding the supplied
flyer's 15 October date. No submission, fee payment or author approval is implied.

## Scientific changes

The original computational results and manuscript are retained. This paper adds
explicitly post-hoc comparisons against training-threshold periodicity and interval
CV rules, all six leave-one-feature-out models, and 25%/75% target coverage. Saved
primary predictions are reproduced to numerical tolerance before these results
are written. The selected record set is identical. New outputs are in
`results/gate_sensitivity.csv`, `gate_sensitivity_predictions.csv`,
`participant_coverage.csv` and `extended_summary.json`.

The full model retains 159 of 316 eligible records from 29 of 32 participants;
RMSSD MAE is 6.00 ms. The 299 eligible records from those same 29 participants
have MAE 15.36 ms. The all-32-participant baseline is 15.33 ms. These estimands
must not be interchanged. Feature removal does not establish that every feature
is necessary, and the univariate comparisons retain different participant sets.

## Rebuild

Run the analysis commands in the root README using the recorded research
environment. `make_figures.py` also requires the downloaded WFDB data for the
event examples. It exports SVG and PDF vector files, plus 400 dpi PNG fallbacks.

The document builder requires Python, pandas, python-docx and lxml. In Codex,
resolve and use the bundled document runtime. Elsewhere, install these packages
in an isolated environment. The builder reads the retained macro-free reference
and preserves all template package parts except explicitly editable content,
relationships and metadata. The original macro-enabled sample is never executed.

```powershell
python paper/build_paper.py
./paper/export_word.ps1 -InputFile "$PWD/paper/ICIIPC2026_Heart_Sound_Variability.docx" -OutputPdf "$PWD/paper/ICIIPC2026_Heart_Sound_Variability.pdf"
```

The export helper uses installed Microsoft Word in the background, with macros
disabled, read-only input and no external transmission. The standard Codex DOCX
renderer was attempted but bundled LibreOffice is unavailable on this Windows
host. Word export plus bundled Poppler was used for visual QA instead. The source
template's page geometry and paragraph styles are retained. See `artifact.md`.

Bibliographic metadata are cached in `reference_metadata.json` from Crossref's
publisher deposits. Optional `fetch_references.py` refreshes those records over
the network. Dataset DOIs, HSMM issue metadata and the PhysioNet reference were
cross-checked against primary pages. Do not run a metadata refresh implicitly
when reproducing a historical paper.

## Author review before submission

Names and affiliations were supplied by the user. The corresponding author and
email have not been provided. Funding, conflicts, contributions and institutional
ethics determinations require the actual investigators' confirmation; none are
invented.

This is an exploratory computational manuscript. It has no expert ECG/S1/S2
adjudication, recognized segmentation benchmark or external validation. It does
not establish clinical HRV equivalence. Those limits are stated in the paper.
No Turnitin/iThenticate check was run, and no similarity or AI-detection score is
guaranteed. The conference advertises an iThenticate similarity limit of 10%;
similarity and AI-detection outputs are different assessments.

## Verification

- Ten scientific/interface tests passed, including held-out target perturbation,
  held-out feature perturbation of training thresholds, and participant-overlap
  rejection.
- All 2,704 source-file checksums and 32 participant folds passed the audit.
- Original primary predictions and acceptance decisions were reproduced.
- All final PDF pages were visually inspected for clipping, tables, figures,
  equation rendering and references; numerical tables are generated from results.

QA images and downloaded macro-enabled templates stay local and are ignored by
Git. `submission_checks.json` records the final document inspection and hashes.
