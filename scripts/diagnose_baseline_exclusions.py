from pathlib import Path
import json
import numpy as np,pandas as pd,mne
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import welch
mne.set_log_level('ERROR')
root=Path.cwd();out=root/'outputs/exclusion_investigation';out.mkdir(exist_ok=True)
base=root/'outputs/baseline_2026-11-10_145427_EST/master_preprocessing'
settings=json.loads((base/'preprocessing_settings.json').read_text()); names=settings['shared_channels']
rows=pd.read_csv(base/'recording_qc.csv').drop(columns=['diagnosis'])
summaries=[];channel_rows=[];epoch_rows=[];unit_rows=[]
reps={'sub-1448','sub-2237A','sub-2015','sub-2276A','sub-2290A','sub-2431A','sub-2235A','sub-2267A'}
for i,row in enumerate(rows.to_dict('records')):
 table=pd.read_csv(row['channels_path'],sep='\t')
 raw=mne.io.read_raw_brainvision(row['header_path'],preload=False,verbose=False)
 # Compare reader values to explicit float32 channel-major decoding, using documented microV.
 binary=np.memmap(row['eeg_path'],dtype='<f4',mode='r',shape=(64,raw.n_times))
 actual=raw.get_data(picks=list(range(60)),start=0,stop=1000)
 error=float(np.max(np.abs(actual-binary[:60,:1000].astype(float)*1e-6)))
 unit_rows.append({'dataset':row['dataset'],'participant_id':row['participant_id'],'reader_vs_float32_microvolt_max_error_v':error,'scalp_units':';'.join(sorted(table.iloc[:60].units.unique()))})
 del binary
 raw.rename_channels(dict(zip(raw.ch_names[:60],table.iloc[:60]['name'].str.upper())))
 raw.pick(names).reorder_channels(names)
 raw.crop(tmax=min(raw.times[-1],300-1/raw.info['sfreq'])).load_data()
 if row['participant_id'] in reps:
  original=raw.get_data(start=0,stop=round(20*raw.info['sfreq']));original_sf=raw.info['sfreq']
 raw.filter(.5,40,method='iir',phase='zero',iir_params={'order':4,'ftype':'butter','output':'sos'},verbose=False)
 raw.resample(200,method='fft',verbose=False);raw.crop(tmin=2,tmax=raw.times[-1]-2)
 data=mne.make_fixed_length_epochs(raw,duration=4,preload=True,verbose=False).get_data(copy=False)
 ptp=np.ptp(data,axis=-1)*1e6; after=data-data.mean(axis=1,keepdims=True);post_ptp=np.ptp(after,axis=-1)*1e6
 pre_high=ptp>200;pre_flat=ptp<1;post_high=post_ptp>200;post_flat=post_ptp<1
 pre_ok=~(pre_high|pre_flat).any(axis=1); post_ok=~(post_high|post_flat).any(axis=1);keep=pre_ok&post_ok
 assert keep.sum()==row['retained_epochs'],row['participant_id']
 common={k:row[k] for k in ['dataset','participant_id','recording_id']}
 summaries.append({**common,'baseline_included':row['included'],'candidate_epochs':len(data),'pre_high_failed':int(pre_high.any(axis=1).sum()),'pre_flat_failed':int(pre_flat.any(axis=1).sum()),'pre_pass':int(pre_ok.sum()),'post_candidates':int(pre_ok.sum()),'post_high_failed':int((post_high.any(axis=1)&pre_ok).sum()),'post_flat_failed':int((post_flat.any(axis=1)&pre_ok).sum()),'kept':int(keep.sum()),'usable_seconds':int(keep.sum()*4)})
 for c,name in enumerate(names):
  channel_rows.append({**common,'channel':name,'candidate_epochs':len(data),'pre_high_failed':int(pre_high[:,c].sum()),'pre_flat_failed':int(pre_flat[:,c].sum()),'pre_median_ptp_uv':float(np.median(ptp[:,c])),'post_candidates':int(pre_ok.sum()),'post_high_failed':int((post_high[:,c]&pre_ok).sum()),'post_flat_failed':int((post_flat[:,c]&pre_ok).sum())})
 for e in range(len(data)):
  epoch_rows.append({**common,'epoch_index':e,'onset_seconds':2+4*e,'pre_high_channels':';'.join(np.array(names)[pre_high[e]]),'pre_flat_channels':';'.join(np.array(names)[pre_flat[e]]),'post_evaluated_sequentially':bool(pre_ok[e]),'post_high_channels_all_candidates':';'.join(np.array(names)[post_high[e]]),'post_flat_channels_all_candidates':';'.join(np.array(names)[post_flat[e]]),'kept':bool(keep[e])})
 if row['participant_id'] in reps:
  failing=np.argmax((pre_high|pre_flat).sum(axis=0));view=list(dict.fromkeys([names[failing],'FP1','FP2','CZ','OZ']))
  fig,axs=plt.subplots(2,2,figsize=(13,7));e=int(np.argmax((pre_high|pre_flat).sum(axis=1)))
  for name in view:
   c=names.index(name);axs[0,0].plot(np.arange(original.shape[1])/original_sf,original[c]*1e6,label=name,lw=.5)
   axs[0,1].plot(np.arange(800)/200,data[e,c]*1e6,label=name,lw=.7)
   axs[1,0].plot(np.arange(800)/200,after[e,c]*1e6,label=name,lw=.7)
  axs[0,0].set(title='Raw first 20 s',xlabel='s',ylabel='µV');axs[0,1].set(title=f'Filtered candidate epoch {e} (onset {2+4*e}s)',xlabel='s',ylabel='µV')
  axs[1,0].set(title='Same epoch after average reference (diagnostic)',xlabel='s',ylabel='µV')
  for a in axs.flat[:3]:a.legend(fontsize=7)
  for label,arr,fs in [('raw',original,original_sf),('filtered',data.transpose(1,0,2).reshape(49,-1),200),('average reference',after.transpose(1,0,2).reshape(49,-1),200)]:
   f,p=welch(arr,fs=fs,nperseg=round(fs*2),noverlap=round(fs),axis=-1)
   use=(f>=1)&(f<=80);axs[1,1].semilogy(f[use],p.mean(axis=0)[use]*1e12,label=label)
  axs[1,1].set(title='Mean scalp PSD (all candidates; not clean-only)',xlabel='Hz',ylabel='µV²/Hz');axs[1,1].legend()
  fig.suptitle(f"{row['dataset']} / {row['participant_id']} — baseline {'retained' if row['included'] else 'excluded'}, {keep.sum()}/74 epochs")
  fig.tight_layout();fig.savefig(out/f"diagnostic_{row['participant_id']}.png",dpi=130);plt.close(fig)
 raw.close()
 if (i+1)%20==0:print('Diagnosed',i+1,flush=True)
pd.DataFrame(summaries).to_csv(out/'baseline_stage_counts.csv',index=False)
pd.DataFrame(channel_rows).to_csv(out/'baseline_channel_causes.csv',index=False)
pd.DataFrame(epoch_rows).to_csv(out/'baseline_epoch_causes.csv',index=False)
pd.DataFrame(unit_rows).to_csv(out/'reader_unit_checks.csv',index=False)
print(pd.DataFrame(summaries).groupby('dataset').sum(numeric_only=True).to_string(),flush=True)
