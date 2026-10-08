"""Frozen exploratory gross price diagnostics. Not a trading backtest."""
import json
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(__file__).resolve().parent
b=json.loads((ROOT/'CRT_research/data/Claude_split_boundaries_EURUSD.json').read_text())
def epoch(s): return int(datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp())
a=np.load(ROOT/'raw_data/Claude_EURUSD_20260930/H1.npy')
a=a[(a['time']>=epoch(b['train_start']))&(a['time']<=epoch(b['val_end']))]
names=['last_candle_direction','three_bar_direction','breakout_20','failed_breakout_20']
results=[]
for split,start,end in [('TRAIN',b['train_start'],b['train_end']),('VALIDATION',b['val_start'],b['val_end'])]:
 x=a[(a['time']>=epoch(start))&(a['time']<=epoch(end))]
 o,h,l,c=(x[k].astype(float) for k in ['open','high','low','close'])
 sig={k:np.zeros(len(x),dtype=int) for k in names}
 for i in range(20,len(x)):
  if np.any(np.diff(x['time'][i-20:i+1])!=3600): continue
  hi=max(h[i-20:i]); lo=min(l[i-20:i])
  sig['last_candle_direction'][i]=int(np.sign(c[i]-o[i]))
  sig['three_bar_direction'][i]=int(np.sign(c[i]-c[i-3]))
  sig['breakout_20'][i]=1 if c[i]>hi else -1 if c[i]<lo else 0
  sig['failed_breakout_20'][i]=-1 if h[i]>hi and lo<=c[i]<=hi and l[i]>=lo else 1 if l[i]<lo and lo<=c[i]<=hi and h[i]<=hi else 0
 for name in names:
  for horizon in [1,3,6]:
   values=[]; directions=[]
   for i in np.where(sig[name]!=0)[0]:
    j=i+1; k=i+horizon
    if k>=len(x) or np.any(np.diff(x['time'][i:k+1])!=3600): continue
    values.append(sig[name][i]*(c[k]-o[j])/1e-4); directions.append(int(sig[name][i]))
   v=np.array(values); d=np.array(directions)
   ci=None
   if len(v)>=120:
    rng=np.random.default_rng(20260930); means=[]
    for _ in range(2000):
     starts=rng.integers(0,len(v),size=(len(v)+119)//120)
     sample=v[(starts[:,None]+np.arange(120))%len(v)].ravel()[:len(v)]
     means.append(float(sample.mean()))
    ci=np.quantile(means,[.025,.975]).tolist()
   r={'split':split,'condition':name,'horizon_H1_bars':horizon,'observations':len(v),
    'mean_signed_pips':float(v.mean()) if len(v) else None,'median_signed_pips':float(np.median(v)) if len(v) else None,
    'CI95_exploratory_block':ci,'bull_observations':int(np.sum(d==1)),'bear_observations':int(np.sum(d==-1)),
    'bull_mean_pips':float(v[d==1].mean()) if np.any(d==1) else None,
    'bear_mean_pips':float(v[d==-1].mean()) if np.any(d==-1) else None}
   results.append(r)
   print(split,name,horizon,len(v),round(r['mean_signed_pips'],3) if len(v) else None,ci,flush=True)
(OUT/'Claude_price_behavior_results.json').write_text(json.dumps({'OOS_evaluated':False,'gross_only':True,'results':results},indent=2))
