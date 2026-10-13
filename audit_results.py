"""Audit cohort coverage, fold isolation and timing plots after analysis."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
import wfdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analysis import ROOT,DATA,OUT,acoustic,ecg_reference,band

manifest=json.loads((DATA/'manifest.json').read_text())
assert len(manifest)==2704
for item in manifest:
    assert hashlib.sha256((DATA/item['file']).read_bytes()).hexdigest()==item['sha256']
d=pd.read_csv(OUT/'records.csv');p=pd.read_csv(OUT/'heldout_predictions.csv')
assert len(d)==338 and d.subject.nunique()==32
assert not d.record.duplicated().any()
folds=json.loads((OUT/'fold_audit.json').read_text())
for fold in folds:
    assert fold['heldout_subject'] not in fold['training_subjects']
    assert len(set(fold['training_subjects']))==p.subject.nunique()-1
assert len(folds)==p.subject.nunique()
assert p.prediction.notna().all()
d['included_in_primary']=d.record.isin(set(p.record))
d['exclusion_reason']=''
d.loc[~d.reference_ok,'exclusion_reason']='ECG comparator check failed'
d.loc[d.reference_ok & ~d.included_in_primary,'exclusion_reason']='Missing audio metric or gate feature'
d[['record','subject','condition','status','ecg_crosslead_f1','included_in_primary','exclusion_reason']].to_csv(OUT/'cohort_flow.csv',index=False)
assert d.identity_max_error_s.dropna().max()<1e-12
q=p.sort_values('abs_rmssd_error')
chosen=q.iloc[[0,len(q)//2,len(q)-1]]
fig,ax=plt.subplots(3,2,figsize=(14,9))
for i,(_,row) in enumerate(chosen.iterrows()):
    er=wfdb.rdrecord(str(DATA/'WFDB'/(row.record+'_ecg')))
    pr=wfdb.rdrecord(str(DATA/'WFDB'/(row.record+'_pcg')))
    r,f1=ecg_reference(er.p_signal);a,_,_,env=acoustic(pr.p_signal[:,0])
    tt=np.arange(pr.sig_len)/1000
    for j,(y,events,title) in enumerate([(band(er.p_signal[:,1],5,25),r,'ECG lead II'),(env,a,'PCG envelope; independent acoustic events')]):
        ax[i,j].plot(tt,y,lw=.6)
        events=events[(events>=2)&(events<10)]
        ax[i,j].scatter(events,y[(events*1000).astype(int)],s=18,color='red')
        ax[i,j].set(xlim=(2,10),xlabel='Time (s)',title=f'{row.record}: {title}')
    ax[i,0].set_ylabel(f'RMSSD error {row.abs_rmssd_error:.1f} ms')
fig.suptitle('Audit examples selected by lowest, median and highest RMSSD error (not expert adjudication)')
fig.tight_layout();fig.savefig(OUT/'signal_audit.png',dpi=160)
audit=dict(checksum_files=len(manifest),records=len(d),subjects=int(d.subject.nunique()),folds=len(folds),
    extraction_status=d.status.value_counts().to_dict(),duration_s=[float(d.duration_s.min()),float(d.duration_s.max())],
    before_after_counts=d.condition.value_counts().to_dict(),identity_max_error_s=float(d.identity_max_error_s.max()),
    eligible_metadata_hr_abs_difference_median=float(np.median(abs(p.ecg_hr-p.metadata_hr))),
    automated_checks_passed=True,expert_annotations=False)
(OUT/'audit.json').write_text(json.dumps(audit,indent=2))
print(json.dumps(audit,indent=2))
