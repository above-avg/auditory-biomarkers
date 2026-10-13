"""Publication figures generated exclusively from measured repository outputs."""
from pathlib import Path
import sys,json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analysis import acoustic,ecg_reference,band,DATA
import wfdb

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'figures'; OUT.mkdir(exist_ok=True)
RESULTS=ROOT.parent/'results'
d=pd.read_csv(RESULTS/'heldout_predictions.csv')
s=json.loads((RESULTS/'summary.json').read_text())
g=pd.read_csv(RESULTS/'gate_sensitivity.csv')
p=pd.read_csv(RESULTS/'participant_coverage.csv')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':11,
                     'axes.labelsize':10,'axes.spines.top':False,'axes.spines.right':False,
                     'svg.fonttype':'path','pdf.fonttype':42,'axes.axisbelow':True})
TEAL='#147D80'; RED='#C85A42'; GRAY='#68737D'; INK='#182938'
def save(fig,name):
    for suffix in ['png','svg','pdf']:
        fig.savefig(OUT/f'{name}.{suffix}',dpi=400,bbox_inches='tight',facecolor='white')
    plt.close(fig)

fig,ax=plt.subplots(figsize=(7.3,4.15));ax.set(xlim=(0,10),ylim=(0,6));ax.axis('off')
def box(x,y,w,h,text,color='#EDF5F5'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.08,rounding_size=.08',
                              fc=color,ec=INK,lw=.8))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=9.8,color=INK)
def arrow(a,b):ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='->',color=INK,lw=1.1))
box(.1,4.75,2.65,.9,'Source: 338 records\n32 participants')
box(3.65,4.75,2.7,.9,'Eligible: 316 records\n32 participants')
box(7.2,4.75,2.6,.9,'Retained: 159 records\n29 participants')
arrow((2.85,5.2),(3.55,5.2));arrow((6.45,5.2),(7.1,5.2))
ax.text(5,4.2,'22 excluded by ECG checks',ha='center',color=RED,fontsize=9)
box(.1,2.35,3.9,1.25,'TRAINING: 31 participants\nAudio features + ECG targets\nFit scaler, model and threshold')
box(5.35,2.35,4.45,1.25,'TEST: one unseen participant\nAudio features only\nFrozen model and threshold')
arrow((4.12,3),(5.23,3));ax.text(4.7,3.45,'freeze',ha='center',fontsize=9)
box(.1,.2,3.9,1.25,'Acoustic recurrence\nHR, RMSSD, interval SD\nNo ECG during extraction')
box(5.35,.2,4.45,1.25,'Guided acoustic peaks\nECG-conditioned diagnostic\nSeparate from audio inference','#FAEFEA')
arrow((2.05,1.55),(2.05,2.25))
ax.text(5,.0,'Repeat for all 32 participants; evaluate error together with coverage',ha='center',va='top',fontsize=9.5)
save(fig,'fig1_workflow')

fig,axes=plt.subplots(1,2,figsize=(7.2,3.3),layout='constrained')
for ax,metric,unit,title in zip(axes,['hr','rmssd'],['bpm','ms'],['(a) Mean heart rate','(b) Successive interval variability']):
    for mask,label,color,marker in [(~d.accepted,'Withheld',RED,'x'),(d.accepted,'Retained',TEAL,'o')]:
        q=d[mask]
        ax.scatter((q['audio_'+metric]+q['ecg_'+metric])/2,q['audio_'+metric]-q['ecg_'+metric],
                   s=17,c=color,marker=marker,alpha=.72,linewidths=.7,label=label)
    ax.axhline(0,color=INK,lw=.7)
    ax.set(xlabel=f'Mean of PCG and ECG ({unit})',ylabel=f'PCG minus ECG ({unit})',title=title)
    ax.grid(alpha=.16)
axes[0].legend(frameon=False,fontsize=9,loc='upper left')
save(fig,'fig2_agreement')

fig,axes=plt.subplots(2,1,figsize=(7.2,4.5),sharex=True,layout='constrained',gridspec_kw={'height_ratios':[1,1.35]})
x=p.subject.to_numpy()
axes[0].bar(x,p.accepted_records,color=TEAL,label='Retained')
axes[0].bar(x,p.eligible_records-p.accepted_records,bottom=p.accepted_records,color='#E1B8AB',label='Withheld')
axes[0].set(ylabel='Record count',title='(a) Participant coverage');axes[0].legend(ncol=2,frameon=False,fontsize=9)
for _,r in p.iterrows():
    if np.isfinite(r.accepted_mae_ms):
        axes[1].plot([r.subject,r.subject],[r.all_mae_ms,r.accepted_mae_ms],color='#B7BFC4',lw=1)
axes[1].scatter(x,p.all_mae_ms,s=24,facecolors='none',edgecolors=GRAY,label='All eligible')
axes[1].scatter(x,p.accepted_mae_ms,s=23,color=TEAL,label='Retained')
axes[1].set(xlabel='Dataset participant ID',ylabel='RMSSD MAE (ms)',title='(b) Within-participant mean error',xticks=x)
axes[1].tick_params(axis='x',labelsize=8);axes[1].legend(ncol=2,frameon=False,fontsize=9)
axes[1].grid(axis='y',alpha=.18)
save(fig,'fig3_participants')

fig,axes=plt.subplots(1,2,figsize=(7.2,3.35),layout='constrained')
op=g[g.variant.isin(['Full model target 25%','Full model','Full model target 75%'])].sort_values('coverage')
xx=op.coverage.to_numpy()*100; yy=op.mae_ms.to_numpy()
axes[0].errorbar(xx,yy,yerr=np.array([yy-op.ci_low,op.ci_high-yy]),fmt='o-',color=TEAL,capsize=3)
axes[0].errorbar([100],[s['methods']['audio_rmssd']['subject_balanced_mae']],
                 yerr=[[15.3296003784-s['methods']['audio_rmssd']['mae_ci'][0]],[s['methods']['audio_rmssd']['mae_ci'][1]-15.3296003784]],
                 fmt='s',color=GRAY,capsize=3,label='All eligible')
axes[0].set(xlabel='Observed record coverage (%)',ylabel='Participant-balanced MAE (ms)',title='(a) Training-threshold operating points',xlim=(15,107),ylim=(0,22))
axes[0].legend(frameon=False,fontsize=8);axes[0].grid(alpha=.18)
q=g.iloc[:3].iloc[::-1]; labels=['Interval CV rule','Periodicity rule','Full model']
y=np.arange(3);v=q.mae_ms.to_numpy()
axes[1].errorbar(v,y,xerr=np.array([v-q.ci_low,q.ci_high-v]),fmt='o',color=TEAL,capsize=3)
axes[1].set(yticks=y,yticklabels=labels,xlabel='RMSSD MAE (ms)',title='(b) Rules at about 50% coverage',xlim=(0,20),ylim=(-.5,2.5))
axes[1].tick_params(axis='y',labelsize=9);axes[1].grid(axis='x',alpha=.18)
save(fig,'fig4_gates')

fig,axes=plt.subplots(2,1,figsize=(7.2,3.45),layout='constrained')
chosen=d.sort_values('abs_rmssd_error').iloc[[0,-1]]
for ax,(_,r) in zip(axes,chosen.iterrows()):
    er=wfdb.rdrecord(str(DATA/'WFDB'/(r.record+'_ecg')))
    pr=wfdb.rdrecord(str(DATA/'WFDB'/(r.record+'_pcg')))
    ecg,_=ecg_reference(er.p_signal);events,_,_,env=acoustic(pr.p_signal[:,0])
    tt=np.arange(len(env))/1000;mask=(tt>=3)&(tt<=8)
    env=env/max(env[mask].max(),1e-12)
    ax.plot(tt[mask],env[mask],color=GRAY,lw=.8)
    e=events[(events>=3)&(events<=8)]
    ax.scatter(e,env[(e*1000).astype(int)],color=TEAL,s=24,label='Audio event')
    for ri in ecg[(ecg>=3)&(ecg<=8)]:ax.axvline(ri,color=RED,alpha=.6,lw=.7,ls='--')
    ax.set(xlim=(3,8),ylabel='Normalized envelope',title=f'{r.record}  |  RMSSD error {r.abs_rmssd_error:.2f} ms  |  '+('retained' if r.accepted else 'withheld'))
    ax.tick_params(axis='y',labelsize=8)
axes[-1].set_xlabel('Time (s)');axes[0].legend(frameon=False,loc='upper right',fontsize=8)
save(fig,'fig5_events')
print('Generated five figures as PNG, SVG and PDF.')
