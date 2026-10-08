"""Frozen EURUSD structural location study; no entry/profit/OOS calculations."""
import json
from pathlib import Path
from datetime import datetime,timezone
from functools import lru_cache
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; OUT=Path(__file__).resolve().parent
DATA=ROOT/'raw_data/Claude_EURUSD_20260930'; TICKS=ROOT/'raw_data/Claude_EURUSD_preOOS_ticks_02'
B=json.loads((ROOT/'CRT_research/data/Claude_split_boundaries_EURUSD.json').read_text())
def epoch(s): return int(datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp())
CUTOFF=epoch(B['oos_start']); TRAIN_END=epoch(B['val_start']); START=epoch(B['train_start'])
ALPHA=.00625

def direction_states(a):
 n=len(a); sh=np.zeros(n,bool); sl=np.zeros(n,bool)
 for i in range(2,n-2):
  wh=a['high'][i-2:i+3]; wl=a['low'][i-2:i+3]
  sh[i]=a['high'][i]==wh.max() and np.sum(wh==wh.max())==1
  sl[i]=a['low'][i]==wl.min() and np.sum(wl==wl.min())==1
 state=0; high=low=None; out=[]
 for t in range(n):
  j=t-2
  if j>=0:
   if sh[j]: high=float(a['high'][j])
   if sl[j]: low=float(a['low'][j])
  up=high is not None and a['close'][t]>high and state!=1
  down=low is not None and a['close'][t]<low and state!=-1
  if up and down: state=0
  elif up: state=1
  elif down: state=-1
  out.append(state)
 return np.array(out)

def zones_from(a,period,crt):
 zones=[]
 for j in range(len(a)-3):
  base=a[j]; size=float(base['high']-base['low'])
  if size<=0: continue
  d=1 if base['close']<base['open'] else -1 if base['close']>base['open'] else 0
  if not d or d*(a[j+3]['close']-base['close'])<2*size: continue
  low=float(base['low'] if d==1 else base['open']); high=float(base['open'] if d==1 else base['high'])
  confirmed=int(a[j+3]['time'])+period
  start=int(np.searchsorted(crt['time'],confirmed,side='left'))
  touch=np.flatnonzero((crt['high'][start:]>=low)&(crt['low'][start:]<=high))
  first=start+int(touch[0]) if len(touch) else len(crt)
  zones.append({'direction':d,'low':low,'high':high,'confirmed':confirmed,'first_touch_index':first})
 return zones

def fresh_match(z,i,c2,wick_low,wick_high,d):
 return z['direction']==d and z['confirmed']<=int(c2['time']) and z['first_touch_index']>=i and wick_low<=z['high'] and z['low']<=wick_high

@lru_cache(maxsize=3)
def day_ticks(day):
 p=TICKS/(day+'.npz')
 if not p.exists(): return None
 with np.load(p) as z: return z['ticks']

def outcome(start,end,target,invalid,d):
 key=datetime.fromtimestamp(start,timezone.utc).strftime('%Y-%m-%d')
 a=day_ticks(key)
 if a is None: return {'outcome':'NO_TICKS','tick_count':0}
 lo=np.searchsorted(a['time_msc'],start*1000); hi=np.searchsorted(a['time_msc'],end*1000)
 q=a[lo:hi]
 if not len(q): return {'outcome':'NO_TICKS','tick_count':0}
 hit_t=np.flatnonzero(q['bid']>=target if d==1 else q['bid']<=target)
 hit_i=np.flatnonzero(q['bid']<=invalid if d==1 else q['bid']>=invalid)
 ti=int(hit_t[0]) if len(hit_t) else None; ii=int(hit_i[0]) if len(hit_i) else None
 tt=int(q['time_msc'][ti]) if ti is not None else None; it=int(q['time_msc'][ii]) if ii is not None else None
 label='NEITHER'
 if tt is not None and it is not None and tt==it: label='AMBIGUOUS'
 elif ti is not None and (ii is None or ti<ii): label='TARGET_FIRST'
 elif ii is not None: label='INVALID_FIRST'
 reference=None
 return {'outcome':label,'tick_count':len(q),'target_time_msc':tt,'invalid_time_msc':it,
  'first_C3_bid':float(q['bid'][0]),'C3_last_bid':float(q['bid'][-1]),
  'C3_high_bid':float(q['bid'].max()),'C3_low_bid':float(q['bid'].min())}

def detect(crt,zones,htf,htf_period,period):
 records=[]; flags=[]; states=direction_states(htf)
 for i in range(1,len(crt)):
  c1,c2=crt[i-1],crt[i]; body=float(abs(c2['close']-c2['open']))
  lower=c2['low']<c1['low']; upper=c2['high']>c1['high']
  if lower==upper or body==0: continue
  d=1 if lower else -1
  wl=float(c2['low'] if d==1 else max(c2['open'],c2['close']))
  wh=float(min(c2['open'],c2['close']) if d==1 else c2['high'])
  if wh-wl<2*body or not(c1['low']<=c2['close']<=c1['high']): continue
  start=int(c2['time'])+period; end=start+period
  split='TRAIN' if start<TRAIN_END else 'VALIDATION'
  limit=TRAIN_END if split=='TRAIN' else CUTOFF
  if start>=CUTOFF or end>limit:
   flags.append({'c2_open':int(c2['time']),'flag':'SPLIT_BOUNDARY_CENSORED'}); continue
  if i+1>=len(crt) or int(crt[i+1]['time'])!=start:
   flags.append({'c2_open':int(c2['time']),'flag':'MISSING_IMMEDIATE_C3'}); continue
  pos=int(np.searchsorted(htf['time']+htf_period,start,side='right')-1)
  bias=int(states[pos]) if pos>=0 else 0
  matches=[z for z in zones if fresh_match(z,i,c2,wl,wh,d)]
  target=float(c1['high'] if d==1 else c1['low']); invalid=float(c2['low'] if d==1 else c2['high'])
  ref=float(c2['close']); rg=float(c1['high']-c1['low']); td=abs(target-ref); inv=abs(ref-invalid)
  record={'c1_open':int(c1['time']),'c2_open':int(c2['time']),'C3_start':start,'C3_end':end,'split':split,
   'direction':d,'htf_bias':bias,'HTF_close_used':int(htf['time'][pos])+htf_period if pos>=0 else None,
   'B1':bool(matches),'B2':bool(matches) and bias==d,'matching_zones':len(matches),
   'target':target,'invalidation':invalid,'reference':ref,'target_distance':td,'invalidation_distance':inv,
   'ratio':td/inv if inv>0 else None,'scale':inv/rg if rg>0 else None,'target_normalized':td/rg if rg>0 else None,
   'body':body,'wick_body_ratio':(wh-wl)/body,'color_bullish':bool(c2['close']>c2['open']),
   **outcome(start,end,target,invalid,d)}
  if record['outcome']!='NO_TICKS':
   high=record['C3_high_bid']; low=record['C3_low_bid']
   record['MFE_price']=max(0.,high-ref if d==1 else ref-low)
   record['MAE_price']=max(0.,ref-low if d==1 else high-ref)
   record['C3_close_in_C1_range_location']=(record['C3_last_bid']-float(c1['low']))/rg if rg>0 else None
  records.append(record)
 return records,flags

def describe(rows):
 out={'N':len(rows),'bull':sum(r['direction']==1 for r in rows),'bear':sum(r['direction']==-1 for r in rows)}
 if not rows: return out
 for name in ['TARGET_FIRST','INVALID_FIRST','NEITHER','NO_TICKS','AMBIGUOUS']:
  out[name+'_rate']=sum(r['outcome']==name for r in rows)/len(rows)
 for name in ['target_distance','invalidation_distance','ratio','scale','target_normalized','MFE_price','MAE_price','C3_close_in_C1_range_location']:
  vals=[r[name] for r in rows if r.get(name) is not None]
  out[name+'_quantiles']=np.quantile(vals,[.1,.5,.9]).tolist() if vals else None
 return out

def bucket(rows):
 for d in [-1,1]:
  sub=[r for r in rows if r['direction']==d]
  if not sub: continue
  valid=[r for r in sub if r['ratio'] is not None and r['scale'] is not None]
  if len(valid)!=len(sub): raise RuntimeError('Degenerate control geometry; do not relax matching')
  rb=np.percentile([r['ratio'] for r in sub],[33.33,66.67]) if len(sub)>=5 else None
  sb=np.percentile([r['scale'] for r in sub],[33.33,66.67]) if len(sub)>=5 else None
  for r in sub: r['bucket']=(d,int(np.digitize(r['ratio'],rb)) if rb is not None else -1,int(np.digitize(r['scale'],sb)) if sb is not None else -1)

def control(parent,subset):
 if not subset: return None
 if any(r['outcome'] in ['NO_TICKS','AMBIGUOUS'] for r in parent): return {'blocked':'Missing ticks or ambiguous ordering'}
 groups={}; needs={}
 for r in parent: groups.setdefault(r['bucket'],[]).append(r['outcome']=='TARGET_FIRST')
 for r in subset: needs[r['bucket']]=needs.get(r['bucket'],0)+1
 sparse={str(k):len(groups[k]) for k in needs if len(groups[k])<20}
 rng=np.random.default_rng(43); rates=np.zeros(2000)
 for k,n in needs.items():
  if k not in groups: raise RuntimeError('Empty matched stratum; no fallback')
  rates+=rng.choice(np.array(groups[k],float),size=(2000,n),replace=True).sum(axis=1)
 rates/=len(subset); real=np.mean([r['outcome']=='TARGET_FIRST' for r in subset]); null=float(rates.mean()); effect=float(real-null)
 p=float((np.sum(abs(rates-null)>=abs(effect))+1)/2001)
 return {'N':len(subset),'real_rate':float(real),'matched_null_rate':null,'effect_absolute':effect,
  'effect_relative':effect/null if null>1e-9 else None,'p_value':p,'adjusted_p_8':min(1.,8*p),
  'null_95_interval':np.quantile(rates,[.025,.975]).tolist(),'sparse_strata':sparse}

def classify(train,val,nt,nv):
 if nt<30 or nv<30 or train is None or val is None or 'blocked' in train or 'blocked' in val: return 'INCONCLUSIVE (sample/coverage)'
 sig=train['p_value']<ALPHA and val['p_value']<ALPHA
 if sig and train['effect_absolute']>0 and val['effect_absolute']>0 and nt>=100: return 'PROMISING incremental information'
 if sig and train['effect_absolute']<0 and val['effect_absolute']<0: return 'NEGATIVE incremental information'
 if train['p_value']>=ALPHA and val['p_value']>=ALPHA: return 'NO CONFIRMED INCREMENTAL VALUE'
 return 'INCONCLUSIVE (no replicated corrected effect)'

def run():
 coverage=json.loads((OUT/'Claude_corrected_coverage_report_02.json').read_text())
 assert coverage['max_H1_error_points']==0 and not coverage['expected_H1_without_ticks']
 reports=[]
 for label,period,htf_period,crt_file,htf_file in [('Primary',3600,14400,'H1.npy','H4_preOOS.npy'),('Secondary',14400,86400,'H4_preOOS.npy','D1_preOOS.npy')]:
  crt=np.load(DATA/crt_file); crt=crt[(crt['time']>=START)&(crt['time']+period<=CUTOFF)]
  htf=np.load(DATA/htf_file); htf=htf[htf['time']+htf_period<=CUTOFF]
  zones=zones_from(htf,htf_period,crt)
  rows,flags=detect(crt,zones,htf,htf_period,period)
  cell={'structure':label,'zones_created':len(zones),'censored_or_missing_setups':flags,'splits':{}}
  for split,limit in [('TRAIN',TRAIN_END),('VALIDATION',CUTOFF)]:
   a1=[r for r in rows if r['split']==split]; bucket(a1)
   b1=[r for r in a1 if r['B1']]; b2=[r for r in b1 if r['B2']]
   cell['splits'][split]={'A1':describe(a1),'B1':describe(b1),'B2':describe(b2),
    'B1_bull':describe([r for r in b1 if r['direction']==1]),'B1_bear':describe([r for r in b1 if r['direction']==-1]),
    'B2_bull':describe([r for r in b2 if r['direction']==1]),'B2_bear':describe([r for r in b2 if r['direction']==-1]),
    'B1_vs_A1':control(a1,b1),'B2_vs_B1':control(b1,b2),
    'zones_confirmed_by_split_end':sum(z['confirmed']<=limit for z in zones),
    'zones_consumed_by_split_end':sum(z['confirmed']<=limit and z['first_touch_index']<len(crt) and int(crt['time'][z['first_touch_index']])+period<=limit for z in zones)}
   print(label,split,'A1',len(a1),'B1',len(b1),'B2',len(b2),'B1_effect',cell['splits'][split]['B1_vs_A1'],flush=True)
  train=cell['splits']['TRAIN']; val=cell['splits']['VALIDATION']
  cell['B1_verdict']=classify(train['B1_vs_A1'],val['B1_vs_A1'],train['B1']['N'],val['B1']['N'])
  cell['B2_verdict']=classify(train['B2_vs_B1'],val['B2_vs_B1'],train['B2']['N'],val['B2']['N'])
  reports.append(cell)
  (OUT/f'Claude_CRT_SD_01_{label}_observations.json').write_text(json.dumps(rows,indent=2))
  (OUT/'Claude_CRT_SD_01_results.json').write_text(json.dumps({'OOS_evaluated':False,'alpha':ALPHA,'cells':reports},indent=2))
 print('STRUCTURAL RESEARCH COMPLETE; NO PROFIT/ENTRY TEST',flush=True)

if __name__=='__main__': run()
