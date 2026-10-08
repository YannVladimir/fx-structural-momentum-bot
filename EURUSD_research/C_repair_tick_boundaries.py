"""Versioned boundary repair; preserve original archives and exclude endpoint."""
import json,os,time,hashlib
from pathlib import Path
from datetime import datetime,timezone,timedelta
import numpy as np
import MetaTrader5 as m
ROOT=Path(__file__).resolve().parents[1]; OUT=Path(__file__).resolve().parent
SOURCE=ROOT/'raw_data/Claude_EURUSD_preOOS_ticks'
DEST=ROOT/'raw_data/Claude_EURUSD_preOOS_ticks_02'; DEST.mkdir(exist_ok=True)
original=json.loads((OUT/'Claude_continuous_tick_manifest.json').read_text())
INDEX=OUT/'Claude_corrected_tick_manifest_02.json'
state=json.loads(INDEX.read_text()) if INDEX.exists() else {'start_utc':original['start_utc'],'end_exclusive_utc':original['end_exclusive_utc'],'days':{},'OOS_evaluated':False,'source_preserved':str(SOURCE)}
def save():
 tmp=INDEX.with_suffix('.tmp'); tmp.write_text(json.dumps(state,indent=2))
 for attempt in range(20):
  try:
   os.replace(tmp,INDEX); return
  except PermissionError:
   if attempt==19: raise
   time.sleep(.1)
assert m.initialize(timeout=15000),m.last_error()
try:
 for key,rec in sorted(original['days'].items()):
  dest=DEST/(key+'.npz')
  if key in state['days'] and (state['days'][key]['status']!='saved' or dest.exists()): continue
  if rec['status']!='saved': state['days'][key]=rec; save(); continue
  end=datetime.fromisoformat(rec['end_exclusive_utc']); begin=end-timedelta(seconds=10)
  # Request the exact endpoint, then explicitly enforce [start,end) locally.
  # Any returned endpoint quote is discarded before calculations or storage.
  tail=m.copy_ticks_range('EURUSD',begin,end,m.COPY_TICKS_ALL)
  if tail is None: raise RuntimeError('Tail retrieval failed '+key+' '+str(m.last_error()))
  lo=int(begin.timestamp()*1000); hi=int(end.timestamp()*1000)
  tail=tail[(tail['time_msc']>=lo)&(tail['time_msc']<hi)]
  with np.load(SOURCE/(key+'.npz')) as old: ticks=old['ticks']
  removed=ticks[ticks['time_msc']>=lo]; ticks=np.concatenate([ticks[ticks['time_msc']<lo],tail])
  if not len(ticks) or np.any(np.diff(ticks['time_msc'])<0) or np.any((ticks['bid']<=0)|(ticks['ask']<ticks['bid'])):
   raise RuntimeError('Invalid repair '+key)
  payload={'ticks':ticks}
  for tf,seconds in [('M1',60),('M5',300),('H1',3600)]:
   bucket=ticks['time']//seconds*seconds
   times,first,count=np.unique(bucket,return_index=True,return_counts=True); last=first+count-1
   bars=np.empty(len(times),dtype=[('time','i8'),('open','f8'),('high','f8'),('low','f8'),('close','f8'),('tick_count','i8')])
   bars['time']=times; bars['open']=ticks['bid'][first]; bars['close']=ticks['bid'][last]
   bars['high']=np.maximum.reduceat(ticks['bid'],first); bars['low']=np.minimum.reduceat(ticks['bid'],first); bars['tick_count']=count
   payload[tf]=bars
  tmp=dest.with_suffix('.tmp')
  with tmp.open('wb') as f: np.savez_compressed(f,**payload)
  os.replace(tmp,dest)
  state['days'][key]={**rec,'rows':len(ticks),'bytes':dest.stat().st_size,'tail_old_rows':len(removed),'tail_new_rows':len(tail),'rows_added':len(tail)-len(removed),
   'last_tick_msc':int(ticks['time_msc'][-1]),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
  state['status']='repairing'; save()
  if len(state['days'])%50==0: print('repaired_through',key,'days',len(state['days']),flush=True)
 state['status']='repair_complete_reconciliation_required'; save(); print('BOUNDARY REPAIR COMPLETE',flush=True)
except Exception as e:
 state['status']='stopped'; state['error']=str(e); save(); raise
finally: m.shutdown()
