"""Resumable UTC daily pre-OOS tick acquisition; no strategy evaluation."""
import json,os,shutil,time,hashlib
from pathlib import Path
from datetime import datetime,timezone,timedelta
import numpy as np
import MetaTrader5 as m
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(__file__).resolve().parent
DATA=ROOT/'raw_data/Claude_EURUSD_preOOS_ticks'
DATA.mkdir(parents=True,exist_ok=True)
B=json.loads((ROOT/'CRT_research/data/Claude_split_boundaries_EURUSD.json').read_text())
def utc(s): return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)
START=utc(B['train_start']); END=utc(B['oos_start'])
INDEX=OUT/'Claude_continuous_tick_manifest.json'
state=json.loads(INDEX.read_text()) if INDEX.exists() else {'start_utc':START.isoformat(),'end_exclusive_utc':END.isoformat(),'days':{},'OOS_evaluated':False}
assert state['start_utc']==START.isoformat() and state['end_exclusive_utc']==END.isoformat()
def save():
 temp=INDEX.with_suffix('.tmp'); temp.write_text(json.dumps(state,indent=2)); os.replace(temp,INDEX)
assert m.initialize(timeout=15000),m.last_error()
start_clock=time.monotonic(); count=0
try:
 day=START
 while day<END:
  finish=min(day+timedelta(days=1),END); key=day.strftime('%Y-%m-%d')
  filename=DATA/(key+'.npz')
  prior=state['days'].get(key,{})
  if prior.get('status')=='saved' and filename.exists():
   day+=timedelta(days=1); continue
  if prior.get('status')=='no_ticks_returned':
   day+=timedelta(days=1); continue
  if shutil.disk_usage(DATA).free<10*1024**3: raise RuntimeError('Stopped before using final 10 GiB free disk space')
  rec={'start_utc':day.isoformat(),'end_exclusive_utc':finish.isoformat()}
  source=ROOT/'raw_data/Claude_EURUSD_20260930'/('ticks_day_'+key+'.npy')
  ticks=np.load(source) if source.exists() else None
  if ticks is None:
   for attempt in range(3):
    ticks=m.copy_ticks_range('EURUSD',day,finish-timedelta(milliseconds=1),m.COPY_TICKS_ALL)
    if ticks is not None: break
    rec['last_error']=str(m.last_error())
    m.shutdown(); m.initialize(timeout=15000)
  if ticks is None:
   rec['status']='request_failed'; state['days'][key]=rec; save()
   raise RuntimeError('MT5 request failed '+key+' '+str(m.last_error()))
  if not len(ticks):
   rec.update(status='no_ticks_returned',rows=0,weekday=day.weekday(),note='Market closure or missing history; not yet distinguished')
  else:
   lower=int(day.timestamp()*1000); upper=int(finish.timestamp()*1000)
   if np.any((ticks['time_msc']<lower)|(ticks['time_msc']>=upper)): raise RuntimeError('Out-of-request-range ticks '+key)
   if np.any(np.diff(ticks['time_msc'])<0): raise RuntimeError('Unordered ticks '+key)
   invalid=int(np.sum((ticks['bid']<=0)|(ticks['ask']<ticks['bid'])))
   if invalid: raise RuntimeError('Invalid Bid/Ask quotes '+key)
   payload={'ticks':ticks}
   for tf,seconds in [('M1',60),('M5',300),('H1',3600)]:
    buckets=ticks['time']//seconds*seconds
    times,first,counts=np.unique(buckets,return_index=True,return_counts=True); last=first+counts-1
    bars=np.empty(len(times),dtype=[('time','i8'),('open','f8'),('high','f8'),('low','f8'),('close','f8'),('tick_count','i8')])
    bars['time']=times; bars['open']=ticks['bid'][first]; bars['close']=ticks['bid'][last]
    bars['high']=np.maximum.reduceat(ticks['bid'],first); bars['low']=np.minimum.reduceat(ticks['bid'],first); bars['tick_count']=counts
    payload[tf]=bars
   tmp=filename.with_suffix('.tmp')
   with tmp.open('wb') as f: np.savez_compressed(f,**payload)
   os.replace(tmp,filename)
   spread=(ticks['ask']-ticks['bid'])/1e-5
   rec.update(status='saved',rows=len(ticks),bytes=filename.stat().st_size,first_tick_msc=int(ticks['time_msc'][0]),last_tick_msc=int(ticks['time_msc'][-1]),
    invalid_quotes=invalid,M1_bars=len(payload['M1']),M5_bars=len(payload['M5']),
    spread_points_quantiles=np.quantile(spread,[.5,.9,.99,1]).tolist(),
    zero_spread_fraction=float(np.mean(spread==0)),sha256=hashlib.sha256(filename.read_bytes()).hexdigest())
  state['days'][key]=rec; state['last_updated_utc']=datetime.now(timezone.utc).isoformat(); state['status']='downloading'; save()
  count+=1
  print(key,rec['status'],rec.get('rows',0),'new_days',count,'elapsed_seconds',round(time.monotonic()-start_clock,1),flush=True)
  day+=timedelta(days=1)
 state['status']='acquisition_complete_coverage_not_yet_validated'; save()
 print('ACQUISITION COMPLETE; COVERAGE AUDIT REQUIRED',flush=True)
except Exception as e:
 state['status']='stopped'; state['error']=str(e); save(); raise
finally: m.shutdown()
