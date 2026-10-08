"""Data/execution audit only; no strategy outcomes or OOS evaluation."""
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
import numpy as np
import MetaTrader5 as mt5

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'raw_data/Claude_EURUSD_20260930'
OUT=Path(__file__).resolve().parent
bound=json.loads((ROOT/'CRT_research/data/Claude_split_boundaries_EURUSD.json').read_text())
def utc(s): return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)
cut=int(utc(bound['oos_start']).timestamp())
report={'created_utc':datetime.now(timezone.utc).isoformat(),'OOS_outcomes_evaluated':False,
        'candles':{},'history_requests':{},'tick_probes':[]}
assert mt5.initialize(timeout=15000),mt5.last_error()
try:
 info=mt5.symbol_info('EURUSD')
 assert info is not None,'EURUSD unavailable'
 report['symbol_properties']={k:getattr(info,k) for k in ['digits','point','trade_tick_size','trade_tick_value','trade_contract_size','volume_min','volume_max','volume_step','trade_stops_level','spread','swap_mode','swap_long','swap_short','swap_rollover3days']}
 report['commission']='Not established from symbol properties; actual account tariff required'
 # UTC-aware range requests bounded to existing research dates; no outcomes examined.
 for label in ['H4','D1']:
  a=mt5.copy_rates_range('EURUSD',getattr(mt5,'TIMEFRAME_'+label),utc(bound['train_start']),utc(bound['val_end']))
  if a is None or not len(a):
   report['history_requests'][label]={'error':str(mt5.last_error())}
  else:
   np.save(DATA/(label+'_preOOS.npy'),a)
   report['history_requests'][label]={'rows':len(a),'filename':label+'_preOOS.npy'}
  print(label,report['history_requests'][label],flush=True)
  (OUT/'Claude_data_audit.json').write_text(json.dumps(report,indent=2))
 # Fixed weekday probes in TRAIN/VALIDATION only. Absence does not establish history start.
 for date in ['2022-11-08','2023-06-06','2024-06-04','2025-06-03','2025-12-02']:
  start=utc(date+'T12:00:00'); end=start+timedelta(minutes=15)
  a=mt5.copy_ticks_range('EURUSD',start,end,mt5.COPY_TICKS_ALL)
  rec={'start_utc':start.isoformat(),'end_utc':end.isoformat()}
  if a is None or not len(a): rec['error']=str(mt5.last_error())
  else:
   np.save(DATA/('ticks_probe_'+date+'.npy'),a)
   valid=(a['bid']>0)&(a['ask']>=a['bid'])
   rec.update(rows=len(a),invalid_quotes=int(np.sum(~valid)),
    first_tick_utc=datetime.fromtimestamp(int(a['time'][0]),timezone.utc).isoformat(),
    last_tick_utc=datetime.fromtimestamp(int(a['time'][-1]),timezone.utc).isoformat(),
    spread_points_quantiles=np.quantile((a['ask'][valid]-a['bid'][valid])/info.point,[.5,.9,.99,1]).tolist() if valid.any() else [])
  report['tick_probes'].append(rec)
  print('tick probe',rec,flush=True)
  (OUT/'Claude_data_audit.json').write_text(json.dumps(report,indent=2))
finally: mt5.shutdown()

for file in DATA.glob('*.npy'):
 if file.name.startswith('ticks'): continue
 a=np.load(file); a=a[a['time']<cut]
 if not len(a):
  report['candles'][file.name]={'preOOS_rows':0}; continue
 dif=np.diff(a['time'])
 nominal={'M1':60,'M5':300,'M15':900,'H1':3600,'H4':14400,'D1':86400}[file.stem.split('_')[0]]
 report['candles'][file.name]={'preOOS_rows':len(a),'duplicate_times':int(len(a)-len(np.unique(a['time']))),
  'nonincreasing_times':int(np.sum(dif<=0)),
  'invalid_ohlc':int(np.sum((a['high']<np.maximum(a['open'],a['close']))|(a['low']>np.minimum(a['open'],a['close']))|(a['high']<a['low']))),
  'gaps_above_nominal':int(np.sum(dif>nominal)),
  'gap_note':'Includes normal market closures; not automatically missing data',
  'zero_spread_rows':int(np.sum(a['spread']==0)),
  'start_utc':datetime.fromtimestamp(int(a['time'][0]),timezone.utc).isoformat(),
  'end_utc':datetime.fromtimestamp(int(a['time'][-1]),timezone.utc).isoformat()}
(OUT/'Claude_data_audit.json').write_text(json.dumps(report,indent=2))
print('AUDIT SAVED',OUT/'Claude_data_audit.json',flush=True)
