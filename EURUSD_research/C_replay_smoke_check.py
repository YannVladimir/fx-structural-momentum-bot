"""First chronological trade per old model/split; technical checks, no selection."""
import json
from pathlib import Path
import numpy as np
from datetime import datetime,timezone
from Claude_tick_execution import replay,daily_chunks
ROOT=Path(__file__).resolve().parents[1]; OUT=Path(__file__).resolve().parent
folder=ROOT/'raw_data/Claude_EURUSD_preOOS_ticks_02'
bars=np.load(ROOT/'raw_data/Claude_EURUSD_20260930/H1.npy')
b=json.loads((ROOT/'CRT_research/data/Claude_split_boundaries_EURUSD.json').read_text())
def epoch(s): return int(datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp())
result=[]
for split in ['TRAIN','VALIDATION']:
 for model in ['momentum_12','range_breakout_20','failed_breakout_20']:
  trade=json.loads((OUT/f'Claude_trades_{split}_{model}_1.0.json').read_text())[0]
  entry=int(trade['entry_utc']); i=int(np.searchsorted(bars['time'],entry))
  split_end=epoch(b['train_end'] if split=='TRAIN' else b['val_end'])
  # Original screen holds at most 24 H1 bars and exits at final bar close.
  last=min(i+23,int(np.searchsorted(bars['time'],split_end,side='right'))-1)
  deadline=int(bars['time'][last]+3600)*1000
  rec={'split':split,'model':model,'selection':'first chronological trade, regardless of outcome','old_OHLC_R':trade['r'],
   'levels':'original requested SL/TP unchanged; market entry uses actual quote; actual entry-to-SL defines R',
   'costs':'one point adverse market/stop slippage and one point hypothetical round-trip commission; tariff unverified'}
  try:
   rec['tick_replay']=replay(daily_chunks(folder,entry*1000,deadline+60000),entry*1000,deadline,
       trade['direction'],trade['stop'],trade['target'],1e-5,1e-5)
  except Exception as e: rec['unresolved']=str(e)
  result.append(rec); print(split,model,rec.get('tick_replay',rec.get('unresolved')),flush=True)
(OUT/'Claude_replay_smoke_results.json').write_text(json.dumps({'OOS_evaluated':False,'purpose':'six technical pilot replays, not economic evidence','results':result},indent=2))
