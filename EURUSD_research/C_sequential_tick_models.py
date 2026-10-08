"""Frozen three-model tick comparison. No parameter selection or OOS evaluation."""
import json
from pathlib import Path
from datetime import datetime,timezone,timedelta
from functools import lru_cache
import numpy as np
from Claude_tick_execution import replay,ReplayError
ROOT=Path(__file__).resolve().parents[1]; OUT=Path(__file__).resolve().parent
DATA=ROOT/'raw_data/Claude_EURUSD_preOOS_ticks_02'
B=json.loads((ROOT/'CRT_research/data/Claude_split_boundaries_EURUSD.json').read_text())
coverage=json.loads((OUT/'Claude_corrected_coverage_report_02.json').read_text())
assert not coverage['expected_H1_without_ticks'] and coverage['max_H1_error_points']==0
def epoch(s): return int(datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp())
SCENARIOS=[{'name':'observed_quotes','spread_multiplier':1.,'slippage_points':1,'commission_USD_per_standard_lot_roundtrip':1},
 {'name':'stress_1_5','spread_multiplier':1.5,'slippage_points':2,'commission_USD_per_standard_lot_roundtrip':7},
 {'name':'stress_2','spread_multiplier':2.,'slippage_points':3,'commission_USD_per_standard_lot_roundtrip':7}]
protocol={'models':['momentum_12','range_breakout_20','failed_breakout_20'],'scenarios':SCENARIOS,
 'signal':'exact formulas from Claude_initial_research.py; closed H1; next bar entry',
 'SL_TP':'actual market fill anchored SMA TR14 * 1.5 stop; target 2 distances; unchanged strategy formula',
 'eligibility':'one position; after tick exit, next signal candle is the following H1 bar, matching earlier engine indexing',
 'holding':'24 H1 bars; split-end administrative flatten at last available pre-boundary quote',
 'costs':'Bid/Ask included once. Spread stress widens Ask relative to unchanged Bid. Stop/market slippage adverse; TP ideal resting limit. Commission scenario is hypothetical, not actual tariff.',
 'swap':'not modeled; positive results cannot qualify until swap/account commission verified',
 'OOS_evaluated':False,'splits':B}
(OUT/'Claude_sequential_tick_protocol.json').write_text(json.dumps(protocol,indent=2))
a=np.load(ROOT/'raw_data/Claude_EURUSD_20260930/H1.npy')
a=a[(a['time']>=epoch(B['train_start']))&(a['time']<=epoch(B['val_end']))]
o,h,l,c=(a[k].astype(float) for k in ['open','high','low','close'])
tr=np.maximum(h-l,np.maximum(abs(h-np.roll(c,1)),abs(l-np.roll(c,1)))); tr[0]=h[0]-l[0]
atr=np.full(len(a),np.nan)
for i in range(13,len(a)): atr[i]=tr[i-13:i+1].mean()
signals={name:np.zeros(len(a),dtype=int) for name in protocol['models']}
for i in range(20,len(a)):
 hi=h[i-20:i].max(); lo=l[i-20:i].min()
 signals['momentum_12'][i]=int(np.sign(c[i]-c[i-12]))
 signals['range_breakout_20'][i]=1 if c[i]>hi else -1 if c[i]<lo else 0
 signals['failed_breakout_20'][i]=-1 if h[i]>hi and lo<=c[i]<=hi and l[i]>=lo else 1 if l[i]<lo and lo<=c[i]<=hi and h[i]<=hi else 0

@lru_cache(maxsize=5)
def raw_day(key):
 p=DATA/(key+'.npz')
 if not p.exists():
  manifest=json.loads((OUT/'Claude_corrected_tick_manifest_02.json').read_text())
  if manifest['days'].get(key,{}).get('status')=='no_ticks_returned': return None
  raise ReplayError('Missing tick day '+key)
 with np.load(p) as z: return z['ticks']

def quote_chunks(start,end,mult):
 day=datetime.fromtimestamp(start/1000,timezone.utc).replace(hour=0,minute=0,second=0,microsecond=0)
 assert end<=epoch(B['oos_start'])*1000
 while int(day.timestamp()*1000)<end:
  q=raw_day(day.strftime('%Y-%m-%d'))
  if q is not None:
   q=q[(q['time_msc']>=start)&(q['time_msc']<end)]
   if mult!=1:
    q=q.copy(); q['ask']=q['bid']+(q['ask']-q['bid'])*mult
   if len(q): yield q
  day+=timedelta(days=1)

def metrics(rows):
 r=np.array([x['R'] for x in rows]); w=r[r>0]; loss=r[r<0]
 equity=np.r_[0,r.cumsum()]; dd=np.maximum.accumulate(equity)-equity
 streak=longest=0
 for x in r:
  streak=streak+1 if x<0 else 0; longest=max(longest,streak)
 rng=np.random.default_rng(20260930); means=[]
 if len(r)>=20:
  for _ in range(2000):
   starts=rng.integers(0,len(r),size=(len(r)+19)//20)
   sample=r[(starts[:,None]+np.arange(20))%len(r)].ravel()[:len(r)]
   means.append(float(sample.mean()))
 stops=np.array([x['R'] for x in rows if x['reason']=='stop'])
 return {'trades':len(r),'win_rate':float(np.mean(r>0)) if len(r) else None,
 'expectancy_R':float(r.mean()) if len(r) else None,'PF':float(w.sum()/(-loss.sum())) if len(loss) else None,
 'total_R':float(r.sum()),'max_DD_R':float(dd.max()),'average_win_R':float(w.mean()) if len(w) else None,
 'average_loss_R':float(loss.mean()) if len(loss) else None,'worst_R':float(r.min()) if len(r) else None,
 'max_consecutive_losses':longest,'average_duration_hours':float(np.mean([(x['exit_time_msc']-x['entry_time_msc'])/3600000 for x in rows])) if rows else None,
 'MFE_R_mean':float(np.mean([x['MFE_R'] for x in rows])) if rows else None,'MAE_R_mean':float(np.mean([x['MAE_R'] for x in rows])) if rows else None,
 'stop_count':len(stops),'stop_median_R':float(np.median(stops)) if len(stops) else None,
 'stop_worst_R':float(stops.min()) if len(stops) else None,'stops_worse_than_minus1_5R_fraction':float(np.mean(stops<-1.5)) if len(stops) else None,
 'block20_CI95':np.quantile(means,[.025,.975]).tolist() if means else None}

results=[]
for split,start,end in [('TRAIN',B['train_start'],B['train_end']),('VALIDATION',B['val_start'],B['val_end'])]:
 eligible=np.flatnonzero((a['time']>=epoch(start))&(a['time']<=epoch(end))); last=int(eligible[-1])
 boundary=(int(a['time'][last])+3600)*1000
 lastday=raw_day(datetime.fromtimestamp((boundary-1)/1000,timezone.utc).strftime('%Y-%m-%d'))
 finalquote=int(lastday['time_msc'][np.searchsorted(lastday['time_msc'],boundary)-1])
 for model in protocol['models']:
  for scenario in SCENARIOS:
   rows=[]; i=int(eligible[0]); failures=[]
   while i<last:
    d=int(signals[model][i]); distance=float(atr[i]*1.5)
    if not d or not np.isfinite(distance) or distance<=0: i+=1; continue
    j=i+1; requested=int(a['time'][j])*1000
    maximum=int(a['time'][min(j+23,last)])*1000+3600000
    deadline=min(maximum,finalquote)
    slip=scenario['slippage_points']*1e-5
    first=next(quote_chunks(requested,boundary,scenario['spread_multiplier']))[0]
    entry=float(first['ask'] if d==1 else first['bid'])+d*slip
    stop=entry-d*distance; target=entry+d*2*distance
    try:
     r=replay(quote_chunks(requested,boundary,scenario['spread_multiplier']),requested,deadline,d,stop,target,
         slip,scenario['commission_USD_per_standard_lot_roundtrip']/100000)
    except ReplayError as e:
     failures.append({'signal_epoch':int(a['time'][i]),'error':str(e)})
     raise RuntimeError('Unresolved trade; stop rather than omit: '+str(failures[-1])) from e
    r.update(signal_epoch=int(a['time'][i]),scenario=scenario['name'],split=split,model=model,
             administrative_split_end_exit=bool(r['reason']=='time' and deadline==finalquote))
    rows.append(r)
    exitbar=int(np.searchsorted(a['time'],r['exit_time_msc']/1000,side='right')-1)
    i=exitbar+1
   record={'split':split,'model':model,'scenario':scenario['name'],**metrics(rows),'unresolved_trades':failures}
   results.append(record)
   (OUT/f'Claude_tick_trades_{split}_{model}_{scenario["name"]}.json').write_text(json.dumps(rows,indent=2))
   (OUT/'Claude_sequential_tick_results.json').write_text(json.dumps({'protocol':protocol,'results':results,'status':'running'},indent=2))
   print(split,model,scenario['name'],record['trades'],record['expectancy_R'],record['PF'],flush=True)
(OUT/'Claude_sequential_tick_results.json').write_text(json.dumps({'protocol':protocol,'results':results,'status':'complete'},indent=2))
print('COMPLETE',flush=True)
