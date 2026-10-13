"""Post-hoc quality-gate sensitivity analyses; does not change primary results.

Run after analysis.py. Every threshold is estimated on training participants.
The saved primary predictions must be reproduced before additions are emitted.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from analysis import FEATURES, OUT, cluster_ci


def predict_fold(train, test, features=FEATURES, coverage=.5, rule=None):
    if set(train.subject) & set(test.subject):
        raise ValueError('Training and held-out participants overlap')
    if not 0 < coverage < 1:
        raise ValueError('Coverage must lie strictly between zero and one')
    if rule:
        sign = -1 if rule == 'periodicity' else 1
        training_score = sign * train[rule].to_numpy()
        score = sign * test[rule].to_numpy()
    else:
        model = make_pipeline(StandardScaler(), Ridge(alpha=10))
        weight = 1 / train.groupby('subject').subject.transform('count')
        weight /= weight.mean()
        model.fit(train[features], np.log1p(train.abs_rmssd_error),
                  ridge__sample_weight=weight)
        training_score = model.predict(train[features])
        score = model.predict(test[features])
    threshold = float(np.quantile(training_score, coverage))
    return score, threshold


def evaluate_variant(data, features=FEATURES, coverage=.5, rule=None):
    result = data[['record','subject','condition','abs_rmssd_error']].copy()
    for subject in sorted(data.subject.unique()):
        train, test = data[data.subject != subject], data[data.subject == subject]
        score, threshold = predict_fold(train, test, features, coverage, rule)
        result.loc[test.index, 'score'] = score
        result.loc[test.index, 'threshold'] = threshold
        result.loc[test.index, 'accepted'] = score <= threshold
    result['accepted'] = result.accepted.astype(bool)
    accepted = result[result.accepted]
    means = accepted.groupby('subject').abs_rmssd_error.mean()
    stats = dict(records=len(result), accepted_records=len(accepted),
                 accepted_subjects=len(means), coverage=float(result.accepted.mean()),
                 mae_ms=float(means.mean()), ci_low=cluster_ci(means)[0],
                 ci_high=cluster_ci(means)[1],
                 absent_subjects=sorted(set(result.subject)-set(accepted.subject)))
    return result, stats


def main():
    data = pd.read_csv(OUT/'heldout_predictions.csv')
    predictions, original = evaluate_variant(data)
    np.testing.assert_allclose(predictions.score, data.prediction, rtol=1e-10, atol=1e-10)
    assert np.array_equal(predictions.accepted, data.accepted)
    specs = [('Full model', FEATURES, .5, None),
             ('Periodicity rule', FEATURES, .5, 'periodicity'),
             ('Interval CV rule', FEATURES, .5, 'interval_cv')]
    specs += [(f'Without {feature}', [f for f in FEATURES if f != feature], .5, None)
              for feature in FEATURES]
    specs += [(f'Full model target {int(q*100)}%', FEATURES, q, None) for q in [.25,.75]]
    rows, saved = [], []
    for label, features, target, rule in specs:
        pred, stats = evaluate_variant(data, features, target, rule)
        rows.append(dict(variant=label,target_coverage=target,**stats))
        pred['variant'] = label
        saved.append(pred)
    pd.DataFrame(rows).to_csv(OUT/'gate_sensitivity.csv', index=False)
    pd.concat(saved, ignore_index=True).to_csv(OUT/'gate_sensitivity_predictions.csv',index=False)
    all_means = data.groupby('subject').abs_rmssd_error.mean()
    accepted = data[data.accepted].groupby('subject').abs_rmssd_error.mean()
    by_subject = data.groupby('subject').agg(eligible_records=('record','size'),
                                           accepted_records=('accepted','sum'))
    by_subject['coverage'] = by_subject.accepted_records / by_subject.eligible_records
    by_subject['all_mae_ms'] = all_means
    by_subject['accepted_mae_ms'] = accepted
    by_subject.to_csv(OUT/'participant_coverage.csv')
    flow = pd.read_csv(OUT/'cohort_flow.csv')
    stats = dict(post_hoc=True, primary_predictions_reproduced=True,
                 all_mae_common_subjects=float(all_means.loc[accepted.index].mean()),
                 accepted_record_p95=float(data.loc[data.accepted,'abs_rmssd_error'].quantile(.95)),
                 accepted_record_max=float(data.loc[data.accepted,'abs_rmssd_error'].max()),
                 excluded_reasons=flow.exclusion_reason.value_counts().to_dict(),
                 variants=rows)
    (OUT/'extended_summary.json').write_text(json.dumps(stats,indent=2))
    print(pd.DataFrame(rows)[['variant','accepted_records','accepted_subjects','mae_ms']].to_string(index=False))


if __name__ == '__main__':
    main()
