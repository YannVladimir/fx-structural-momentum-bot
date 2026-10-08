"""Investigate discrepancies without changing existing reference candles."""
import json
from pathlib import Path
from datetime import datetime,timezone,timedelta
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; OUT=Path(__file__).resolve().parent
DATA=ROOT/'raw_data/Claude_EURUSD_preOOS_ticks'
lookup={int(b['time']):b for b in np.load(ROOT/'raw_data/Claude_EURUSD_20260930/H1.npy')}
rows=[]
for f in sorted(DATA.glob('*.npz')):
 with np.load(f) as z:
  bars=z['H1']; ticks=None
  for bar in bars:
   t=int(bar['time']); ref=lookup.get(t)
   if ref is None: continue
   errors={k:float((bar[k]-ref[k])/1e-5) for k in ['open','high','low','close']}
   if max(abs(v) for v in errors.values())<=1.000001: continue
   if ticks is None: ticks=z['ticks']
   q=ticks[(ticks['time']>=t)&(ticks['time']<t+3600)]
   rec={'hour_utc':datetime.fromtimestamp(t,timezone.utc).isoformat(),'error_points':errors,
    'last_tick_time_msc':int(q['time_msc'][-1]),'last_tick_bid':float(q['bid'][-1]),'reference_close':float(ref['close']),
    'seconds_before_hour_end':float((1000*(t+3600)-q['time_msc'][-1])/1000)}
   nxt=DATA/((datetime.fromisoformat(f.stem)+timedelta(days=1)).strftime('%Y-%m-%d')+'.npz')
   if nxt.exists():
    with np.load(nxt) as n:
     first=n['ticks'][0]
     rec['next_day_first_tick_msc']=int(first['time_msc']); rec['next_day_first_bid']=float(first['bid'])
     rec['reference_close_matches_next_day_first_bid']=bool(abs(float(first['bid'])-float(ref['close']))<1e-9)
   rows.append(rec)
report={'OOS_evaluated':False,'discrepancies':len(rows),'all_at_23UTC':all('T23:00:00' in r['hour_utc'] for r in rows),
 'close_only_discrepancies':sum(all(abs(r['error_points'][k])<1e-6 for k in ['open','high','low']) for r in rows),
 'matches_next_day_first_bid':sum(r.get('reference_close_matches_next_day_first_bid',False) for r in rows),'rows':rows,
 'interpretation':'Matching next-day first quote is a diagnostic, not proof of cause; preserve original candles and source ticks.'}
(OUT/'Claude_boundary_investigation.json').write_text(json.dumps(report,indent=2))
print({k:v for k,v in report.items() if k!='rows'})
