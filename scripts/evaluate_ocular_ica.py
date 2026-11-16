from pathlib import Path
import json
import numpy as np,pandas as pd,mne
from scipy.signal import welch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
mne.set_log_level('ERROR');root=Path.cwd();out=root/'outputs/exclusion_investigation';base=root/'outputs/baseline_2026-11-10_145427_EST/master_preprocessing'
names=json.loads((base/'preprocessing_settings.json').read_text())['shared_channels'];rows=pd.read_csv(base/'recording_qc.csv').drop(columns='diagnosis');summary=[]
for pid in ['sub-1448','sub-2009','sub-2237A','sub-2235A','sub-2267A']:
 row=rows[rows.participant_id==pid].iloc[0];table=pd.read_csv(row.channels_path,sep='\t');raw=mne.io.read_raw_brainvision(row.header_path,preload=False,verbose=False)
 raw.rename_channels(dict(zip(raw.ch_names[:60],table.iloc[:60]['name'].str.upper())));raw.pick(names).reorder_channels(names)
 raw.crop(tmax=min(raw.times[-1],300-1/raw.info['sfreq'])).load_data().filter(.5,40,method='iir',phase='zero',iir_params={'order':4,'ftype':'butter','output':'sos'},verbose=False)
 raw.resample(200,method='fft',verbose=False);raw.crop(tmin=2,tmax=raw.times[-1]-2)
 fit=raw.copy().filter(1,None,method='iir',iir_params={'order':4,'ftype':'butter','output':'sos'},verbose=False)
 ica=mne.preprocessing.ICA(n_components=20,method='infomax',fit_params={'extended':True},random_state=27,max_iter=300)
 ica.fit(fit,decim=2,verbose=False)
 _,scores=ica.find_bads_eog(fit,ch_name=['FP1','FP2'],measure='correlation',threshold=.8,verbose=False)
 scores=np.abs(np.asarray(scores));dual=scores.min(axis=0)
 load=np.abs(ica.get_components());frontal=np.array([n.startswith(('FP','AF')) for n in names]);ratio=load[frontal].mean(axis=0)/np.maximum(load[~frontal].mean(axis=0),1e-15)
 eligible=np.flatnonzero((dual>=.8)&(ratio>=3));chosen=[int(eligible[np.argmax(dual[eligible])])] if len(eligible) else []
 clean=ica.apply(raw.copy(),exclude=chosen,verbose=False)
 before=mne.make_fixed_length_epochs(raw,duration=4,preload=True,verbose=False).get_data(copy=False)
 after=mne.make_fixed_length_epochs(clean,duration=4,preload=True,verbose=False).get_data(copy=False)
 def keep(x):
  a=np.ptp(x,axis=-1)*1e6;b=np.ptp(x-x.mean(axis=1,keepdims=True),axis=-1)*1e6
  return ((a<=200)&(a>=1)&(b<=200)&(b>=1)).all(axis=1)
 summary.append({'participant_id':pid,'dataset':row.dataset,'chosen':str(chosen),'max_dual_fp_correlation':float(dual.max()),'chosen_frontal_ratio':float(ratio[chosen[0]]) if chosen else None,'iterations':ica.n_iter_,'baseline_epochs':int(keep(before).sum()),'candidate_epochs':int(keep(after).sum())})
 pd.DataFrame({'component':range(20),'fp1_correlation':scores[0],'fp2_correlation':scores[1],'frontal_loading_ratio':ratio,'selected':np.isin(np.arange(20),chosen)}).to_csv(out/f'ica_pilot_components_{pid}.csv',index=False)
 # Same highest frontal-amplitude epoch before/after; selected without label information.
 e=np.argmax(np.ptp(before[:,names.index('FP1')],axis=-1));fig,axs=plt.subplots(2,2,figsize=(12,7))
 for name in ['FP1','FP2','CZ','OZ']:
  c=names.index(name)
  axs[0,0].plot(np.arange(800)/200,before[e,c]*1e6,label=name,lw=.7);axs[0,1].plot(np.arange(800)/200,after[e,c]*1e6,label=name,lw=.7)
 for ax in axs[0]:ax.legend();ax.set(xlabel='s',ylabel='µV')
 axs[0,0].set_title('Before targeted ICA');axs[0,1].set_title('After candidate ICA (same epoch)')
 for label,arr in [('before',before),('candidate',after)]:
  f,p=welch(arr,fs=200,nperseg=400,noverlap=200,axis=-1);use=(f>=1)&(f<=40)
  axs[1,0].semilogy(f[use],p.mean(axis=(0,1))[use]*1e12,label=label)
 axs[1,0].legend();axs[1,0].set(xlabel='Hz',ylabel='µV²/Hz',title='All candidate epochs, all channels')
 if chosen:
  axs[1,1].bar(range(49),load[:,chosen[0]]);axs[1,1].set_xticks(range(49),names,rotation=90,fontsize=5)
  axs[1,1].set_title('Absolute component loadings (no invented coordinates)')
 else:axs[1,1].text(.1,.5,'No component met the fixed selection rule')
 fig.suptitle(f'{pid}: exploratory ocular-ICA evaluation; component {chosen}');fig.tight_layout();fig.savefig(out/f'ica_pilot_{pid}.png',dpi=130);plt.close(fig)
 print(summary[-1],flush=True)
pd.DataFrame(summary).to_csv(out/'ica_pilot_summary.csv',index=False)
