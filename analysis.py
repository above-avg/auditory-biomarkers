"""Exploratory, subject-held-out acoustic cycle variability benchmark."""
from pathlib import Path
import json, warnings, argparse
import numpy as np
import pandas as pd
from scipy import signal
import wfdb
from wfdb.processing import xqrs_detect
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / 'senssmarttech'
OUT = ROOT / 'results'
FS = 1000
FEATURES = ['periodicity','morphology','interval_cv','peak_cv','detector_disagreement','spectral_ratio']

def band(x, low, high):
    return signal.sosfiltfilt(signal.butter(3, [low,high], fs=FS, btype='bandpass', output='sos'), x)

def metrics(t):
    t=np.asarray(t)
    t=t[(t>=2)&(t<28)]
    ibi = np.diff(t)
    if len(ibi) < 10: return dict(hr=np.nan, rmssd=np.nan, sd=np.nan)
    return dict(hr=60/ibi.mean(), rmssd=1000*np.sqrt(np.mean(np.diff(ibi)**2)), sd=1000*np.std(ibi,ddof=1))

def envelope(x, low=25, high=150):
    y = band(x,low,high)
    return signal.sosfiltfilt(signal.butter(2,15,fs=FS,output='sos'), np.abs(signal.hilbert(y)))

def acoustic(x, low=25, high=150):
    env = envelope(x,low,high)
    z = env-env.mean()
    ac = signal.fftconvolve(z,z[::-1],mode='full')[len(z)-1:]
    ac = ac / np.maximum(np.arange(len(z),0,-1),1)
    ac /= max(ac[0],1e-12)
    candidates,_ = signal.find_peaks(ac[333:1501],prominence=.02)
    candidates = candidates+333
    period = int(candidates[np.argmax(ac[candidates])]) if len(candidates) else int(np.argmax(ac[333:1501])+333)
    peaks,props = signal.find_peaks(env,distance=int(.55*period),prominence=max(np.std(env)*.3,1e-12))
    # Recurrence tracker selects one acoustic phase each cycle, no ECG input.
    candidates2,_ = signal.find_peaks(env,distance=80,prominence=max(np.std(env)*.15,1e-12))
    start = candidates2[candidates2<min(2*period,len(env))]
    if not len(start): raise ValueError('no acoustic events')
    current = int(start[np.argmax(env[start])]); track=[current]
    while current+period < len(env)-200:
        pool=candidates2[(candidates2>current+.65*period)&(candidates2<current+1.35*period)]
        if not len(pool):
            current += period
            continue
        score = np.log(np.maximum(env[pool],1e-12)) - 8*((pool-current-period)/period)**2
        current=int(pool[np.argmax(score)]); track.append(current)
    t=np.array(track)/FS
    t=t[(t>=.5)&(t< len(x)/FS-.5)]
    base=peaks/FS; base=base[(base>=.5)&(base<len(x)/FS-.5)]
    shapes=[]
    for p in (t*FS).astype(int):
        s=env[p-60:p+61]; s=s-s.mean(); shapes.append(s/max(np.linalg.norm(s),1e-12))
    morphology=float(np.mean(np.array(shapes)@np.mean(shapes,axis=0))) if shapes else 0.
    f,p=signal.welch(x,fs=FS,nperseg=2048)
    feat=dict(periodicity=float(ac[period]),morphology=morphology,
        interval_cv=float(np.std(np.diff(t))/max(np.mean(np.diff(t)),1e-12)),
        peak_cv=float(np.std(env[(t*FS).astype(int)])/max(np.mean(env[(t*FS).astype(int)]),1e-12)),
        detector_disagreement=abs(metrics(t)['hr']-metrics(base)['hr']),
        spectral_ratio=float(p[(f>=25)&(f<=150)].sum()/max(p.sum(),1e-12)))
    return t,base,feat,env

def match_f1(a,b,tol=.05):
    i=j=n=0
    while i<len(a) and j<len(b):
        if abs(a[i]-b[j])<=tol: n+=1;i+=1;j+=1
        elif a[i]<b[j]: i+=1
        else: j+=1
    return 2*n/max(len(a)+len(b),1)

def ecg_reference(x):
    ts=[]
    for lead in [0,1]:
        y=band(x[:,lead],5,25)
        y=y/max(np.std(y),1e-12)
        q=xqrs_detect(y,fs=FS,verbose=False)/FS
        ts.append(q[(q>=.5)&(q<len(x)/FS-.5)])
    f1=match_f1(*ts)
    # Lead II is fixed; other lead is a comparator eligibility check.
    return ts[1],f1

def guided(r,env,lo=.015,hi=.160):
    s1=[];s2=[]
    for i in range(len(r)-1):
        a=int((r[i]+lo)*FS);b=int(min(r[i]+hi,r[i+1]-.08)*FS)
        c=int((r[i]+.18)*FS);d=int(min(r[i]+.50,r[i+1]-.06)*FS)
        if b<=a or d<=c: continue
        s1.append((a+np.argmax(env[a:b]))/FS)
        s2.append((c+np.argmax(env[c:d]))/FS)
    return np.asarray(s1),np.asarray(s2)

def pulse(x):
    y=band(x,.5,8)
    p,_=signal.find_peaks(y,distance=280,prominence=.3*np.std(y))
    t=p/FS
    return t[(t>=.5)&(t<len(x)/FS-.5)]

def extract():
    OUT.mkdir(exist_ok=True)
    meta=pd.read_csv(DATA/'Demographics.csv',header=1).iloc[:,:14]
    meta=meta[pd.to_numeric(meta['Subject number'],errors='coerce').notna()]
    rows=[]; beats=[]
    for n,(_,m) in enumerate(meta.iterrows(),1):
        record=str(m['PCG']).removesuffix('_pcg')
        row=dict(record=record,subject=int(m['Subject number']),condition=str(m['Before (B)  / after (A) activity']),metadata_hr=float(m['Median heart rate (bpm)']))
        try:
            er=wfdb.rdrecord(str(DATA/'WFDB'/str(m['ECG'])))
            pr=wfdb.rdrecord(str(DATA/'WFDB'/str(m['PCG'])))
            if er.fs!=FS or pr.fs!=FS or er.sig_len!=pr.sig_len:raise ValueError('Synchronization/sampling mismatch')
            ecg=er.p_signal;pcg=pr.p_signal[:,0]
            row['duration_s']=len(pcg)/FS
            r,f1=ecg_reference(ecg); row['ecg_crosslead_f1']=f1
            rr=np.diff(r)
            row['reference_ok']=bool(f1>=.90 and len(r)>=15 and np.all((rr>=.30)&(rr<=1.5)))
            for k,v in metrics(r).items():row['ecg_'+k]=v
            t,base,feat,env=acoustic(pcg);row.update(feat)
            for label,times in [('audio',t),('peak_baseline',base)]:
                for k,v in metrics(times).items():row[label+'_'+k]=v
            s1,s2=guided(r,env)
            for k,v in metrics(s1).items():row['guided_'+k]=v
            row['guided_delay_sd_ms']=float(np.std(s1-r[:len(s1)],ddof=1)*1000)
            row['guided_systolic_ms']=float(np.median(s2-s1)*1000)
            row['guided_systolic_sd_ms']=float(np.std(s2-s1,ddof=1)*1000)
            # Exact identity diagnostic, using same matched sequence.
            residual=np.diff(s1)-np.diff(r[:len(s1)])
            delay=np.diff(s1-r[:len(s1)])
            row['identity_max_error_s']=float(np.max(np.abs(residual-delay)))
            for b,(ri,si,sii) in enumerate(zip(r,s1,s2)):
                beats.append(dict(record=record,subject=row['subject'],beat=b,r_s=ri,guided_s1_s=si,guided_s2_s=sii))
            for label,low,high in [('audio_band20_200',20,200),('audio_band40_120',40,120)]:
                tt,_,_,_=acoustic(pcg,low,high)
                for k,v in metrics(tt).items():row[label+'_'+k]=v
            for label,lo,hi in [('guided_narrow',.025,.120),('guided_wide',0,.200)]:
                tt,_=guided(r,env,lo,hi)
                for k,v in metrics(tt).items():row[label+'_'+k]=v
            ppg=wfdb.rdrecord(str(DATA/'WFDB'/str(m['PPG']))).p_signal
            for label,ch in [('carotid',0),('brachial',2)]:
                for k,v in metrics(pulse(ppg[:,ch])).items():row[label+'_'+k]=v
            acc=wfdb.rdrecord(str(DATA/'WFDB'/str(m['ACC']))).p_signal[:,0]
            at,_,_,_=acoustic(acc,10,40)
            for k,v in metrics(at).items():row['acc_'+k]=v
            row['status']='ok'
        except Exception as e:row['status']=type(e).__name__+': '+str(e)
        rows.append(row)
        if n%25==0:print(f'Extracted {n}/{len(meta)}',flush=True)
    pd.DataFrame(rows).to_csv(OUT/'records.csv',index=False)
    pd.DataFrame(beats).to_csv(OUT/'guided_beats.csv',index=False)

def cluster_ci(values,seed=20261013):
    a=np.asarray(values,float);a=a[np.isfinite(a)]
    if not len(a): return [None,None]
    rng=np.random.default_rng(seed)
    boot=np.mean(rng.choice(a,(2000,len(a)),replace=True),axis=1)
    return np.quantile(boot,[.025,.975]).tolist()

def evaluate():
    df=pd.read_csv(OUT/'records.csv')
    ok=df['reference_ok'].fillna(False).astype(bool)&df['audio_rmssd'].notna()&df[FEATURES].notna().all(axis=1)
    d=df[ok].copy()
    if d.subject.nunique()<3:raise RuntimeError('Insufficient eligible participants')
    d['abs_rmssd_error']=abs(d.audio_rmssd-d.ecg_rmssd)
    d['prediction']=np.nan;d['accepted']=False
    folds=[]
    for sid in sorted(d.subject.unique()):
        train=d[d.subject!=sid];test=d[d.subject==sid]
        model=make_pipeline(StandardScaler(),Ridge(alpha=10))
        # Equal total training weight per participant.
        weights=1/train.groupby('subject').subject.transform('count')
        weights=weights/weights.mean()
        model.fit(train[FEATURES],np.log1p(train.abs_rmssd_error),ridge__sample_weight=weights)
        threshold=np.quantile(model.predict(train[FEATURES]),.5)
        pred=model.predict(test[FEATURES]);d.loc[test.index,'prediction']=pred
        d.loc[test.index,'accepted']=pred<=threshold
        folds.append(dict(heldout_subject=int(sid),training_subjects=sorted(int(s) for s in train.subject.unique()),
            train_records=len(train),test_records=len(test),threshold=float(threshold),
            coefficients={k:float(v) for k,v in zip(FEATURES,model[-1].coef_)}))
    (OUT/'fold_audit.json').write_text(json.dumps(folds,indent=2))
    d.to_csv(OUT/'heldout_predictions.csv',index=False)
    summary=dict(total_records=len(df),total_subjects=int(df.subject.nunique()),eligible_records=len(d),eligible_subjects=int(d.subject.nunique()),
        failed_records=int((df.status!='ok').sum()),accepted_records=int(d.accepted.sum()),coverage=float(d.accepted.mean()),
        subjects_without_accepted=sorted(set(d.subject)-set(d[d.accepted].subject)),methods={})
    labels=['audio','peak_baseline','guided','carotid','brachial','acc','audio_band20_200','audio_band40_120','guided_narrow','guided_wide']
    rows=[]
    for label in labels:
        for metric in ['hr','rmssd','sd']:
            q=d.dropna(subset=[label+'_'+metric,'ecg_'+metric]).copy()
            e=q[label+'_'+metric]-q['ecg_'+metric]
            means=e.abs().groupby(q.subject).mean()
            stat=dict(records=len(q),subject_balanced_mae=float(means.mean()),mae_ci=cluster_ci(means),record_bias=float(e.mean()),
                descriptive_loa=[float(e.mean()-1.96*e.std()),float(e.mean()+1.96*e.std())])
            summary['methods'][label+'_'+metric]=stat
            rows.append(dict(method=label,metric=metric,**{k:v for k,v in stat.items() if not isinstance(v,list)}))
    allmeans=d.groupby('subject').abs_rmssd_error.mean()
    accmeans=d[d.accepted].groupby('subject').abs_rmssd_error.mean()
    common=allmeans.index.intersection(accmeans.index)
    delta=accmeans.loc[common]-allmeans.loc[common]
    summary['gate']=dict(accepted_subject_balanced_mae=float(accmeans.mean()),mae_ci=cluster_ci(accmeans),
        paired_change_ms=float(delta.mean()),paired_change_ci=cluster_ci(delta),paired_subjects=len(common),
        interpretation='Selection effect on retained recordings; not correction of rejected recordings')
    # Random selection control matches retained counts separately within each subject.
    rng=np.random.default_rng(20261013)
    random_maes=[]
    for _ in range(1000):
        subjmeans=[]
        for sid in common:
            q=d[d.subject==sid].abs_rmssd_error.to_numpy()
            count=int(((d.subject==sid)&d.accepted).sum())
            subjmeans.append(rng.choice(q,count,replace=False).mean())
        random_maes.append(np.mean(subjmeans))
    summary['gate']['matched_random_mae']=float(np.mean(random_maes))
    summary['gate']['matched_random_interval']=np.quantile(random_maes,[.025,.975]).tolist()
    summary['gate']['randomization_fraction_at_or_better']=float((np.sum(np.asarray(random_maes)<=accmeans.mean())+1)/1001)
    phase=d.groupby(['subject','condition']).abs_rmssd_error.mean().unstack()
    if {'A','B'}.issubset(phase.columns):
        paired=(phase.A-phase.B).dropna()
        summary['after_minus_before_error']=dict(subjects=len(paired),mean_ms=float(paired.mean()),ci=cluster_ci(paired))
    strata=[]
    d['hr_band']=pd.cut(d.ecg_hr,[0,90,120,1000],labels=['<90','90-120','>120'],right=False)
    for col in ['condition','hr_band']:
        for val,q in d.groupby(col,observed=True):
            strata.append(dict(stratum=col,value=str(val),records=len(q),subjects=q.subject.nunique(),coverage=q.accepted.mean(),
                rmssd_mae_subject_balanced=q.groupby('subject').abs_rmssd_error.mean().mean()))
    pd.DataFrame(strata).to_csv(OUT/'strata.csv',index=False)
    pd.DataFrame(rows).to_csv(OUT/'method_summary.csv',index=False)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2))
    fig,ax=plt.subplots(1,3,figsize=(15,4))
    for a,metric,unit in zip(ax,['hr','rmssd','sd'],['bpm','ms','ms']):
        a.scatter((d['audio_'+metric]+d['ecg_'+metric])/2,d['audio_'+metric]-d['ecg_'+metric],c=d.accepted.map({True:'teal',False:'coral'}),s=15,alpha=.65)
        a.axhline(0,color='black',lw=.7);a.set(xlabel=f'Mean ({unit})',ylabel=f'Audio - ECG ({unit})',title=metric.upper())
    fig.suptitle('Independent audio baseline: held-out accepted (teal), rejected (coral)')
    fig.tight_layout();fig.savefig(OUT/'agreement.png',dpi=180);plt.close(fig)
    curves=[]
    for coverage in [.25,.5,.75,1]:
        # Post-hoc descriptive rank curve, separately labeled; not deployed threshold performance.
        q=d.nsmallest(max(1,int(len(d)*coverage)),'prediction')
        curves.append(dict(coverage=len(q)/len(d),subject_balanced_mae=q.groupby('subject').abs_rmssd_error.mean().mean()))
    pd.DataFrame(curves).to_csv(OUT/'descriptive_risk_coverage.csv',index=False)
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--evaluate-only',action='store_true');args=parser.parse_args()
    if not args.evaluate_only:extract()
    evaluate()
