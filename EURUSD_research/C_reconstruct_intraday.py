"""Build auditable bid candles from fixed tick samples, never infer missing ticks."""
from pathlib import Path
import json
from datetime import datetime, timezone
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'raw_data/Claude_EURUSD_20260930'
OUT=Path(__file__).resolve().parent
report={'OOS_evaluated':False,'scope':'five fixed historical days, not continuous history','samples':[]}
cost=json.loads((OUT/'Claude_cost_coverage_audit.json').read_text())
for request in cost['intraday_requests']:
 f=DATA/(request['timeframe']+'_probe_'+request['date_utc']+'.npy')
 if not f.exists(): continue
 a=np.load(f)
 start=int(datetime.fromisoformat(request['date_utc']).replace(tzinfo=timezone.utc).timestamp())
 request['out_of_requested_range_rows']=int(np.sum((a['time']<start)|(a['time']>=start+86400)))
 request['usable_rows']=len(a)-request['out_of_requested_range_rows']
 if not request['usable_rows']: request['error']='Out-of-request-range data; exclude file from all research'
(OUT/'Claude_cost_coverage_audit.json').write_text(json.dumps(cost,indent=2))
for f in sorted(DATA.glob('ticks_day_*.npy')):
 a=np.load(f)
 if np.any(np.diff(a['time_msc'])<0): raise RuntimeError('Unordered ticks: '+f.name)
 if np.any((a['bid']<=0)|(a['ask']<a['bid'])): raise RuntimeError('Invalid quotes: '+f.name)
 for tf,seconds in [('M1',60),('M5',300)]:
  bucket=(a['time']//seconds)*seconds
  times,first,count=np.unique(bucket,return_index=True,return_counts=True)
  last=first+count-1
  spread=(a['ask']-a['bid'])/1e-5
  bars=np.empty(len(times),dtype=[('time','i8'),('open','f8'),('high','f8'),('low','f8'),('close','f8'),('tick_volume','i8'),('spread_min_points','f8'),('spread_max_points','f8'),('first_tick_msc','i8'),('last_tick_msc','i8')])
  bars['time']=times; bars['open']=a['bid'][first]; bars['close']=a['bid'][last]
  bars['high']=np.maximum.reduceat(a['bid'],first); bars['low']=np.minimum.reduceat(a['bid'],first)
  bars['tick_volume']=count; bars['spread_min_points']=np.minimum.reduceat(spread,first); bars['spread_max_points']=np.maximum.reduceat(spread,first)
  bars['first_tick_msc']=a['time_msc'][first]; bars['last_tick_msc']=a['time_msc'][last]
  filename=tf+'_from_'+f.stem+'.npy'; np.save(DATA/filename,bars)
  rec={'source':f.name,'timeframe':tf,'bars':len(bars),'missing_clock_buckets_in_day':86400//seconds-len(bars),'output':filename}
  report['samples'].append(rec); print(rec,flush=True)
(OUT/'Claude_reconstructed_intraday_manifest.json').write_text(json.dumps(report,indent=2))
