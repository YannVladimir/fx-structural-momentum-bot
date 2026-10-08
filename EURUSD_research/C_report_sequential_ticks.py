"""Report every completed frozen scenario; retain all trade records."""
import json
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
OUT=Path(__file__).resolve().parent
data=json.loads((OUT/'Claude_sequential_tick_results.json').read_text())
assert data['status']=='complete','Wait for all scenarios'
checks=[]
for rec in data['results']:
 path=OUT/f'Claude_tick_trades_{rec["split"]}_{rec["model"]}_{rec["scenario"]}.json'
 rows=json.loads(path.read_text()); previous=None; monthly={}; yearly={}
 for r in rows:
  assert r['entry_time_msc']>=r['signal_epoch']*1000+3600000,'Signal used before closed'
  assert r['exit_time_msc']>=r['entry_time_msc']
  assert previous is None or r['entry_time_msc']>previous,'Overlapping position'
  previous=r['exit_time_msc']
  assert abs(r['direction']*(r['entry']-r['stop'])-r['initial_risk_price'])<1e-10
  assert abs(r['direction']*(r['target']-r['entry'])-2*r['initial_risk_price'])<1e-10
  date=datetime.fromtimestamp(r['exit_time_msc']/1000,timezone.utc)
  for collection,key in [(monthly,date.strftime('%Y-%m')),(yearly,date.strftime('%Y'))]:
   group=collection.setdefault(key,{'trades':0,'total_R':0.}); group['trades']+=1; group['total_R']+=r['R']
 for collection in [monthly,yearly]:
  for group in collection.values(): group['expectancy_R']=group['total_R']/group['trades']
 checks.append({'split':rec['split'],'model':rec['model'],'scenario':rec['scenario'],'checks_passed':True,
  'administrative_split_end_closes':sum(r['administrative_split_end_exit'] for r in rows),
  'bull_count':sum(r['direction']==1 for r in rows),'bear_count':sum(r['direction']==-1 for r in rows),
  'monthly':monthly,'yearly':yearly})
(OUT/'Claude_sequential_tick_sanity_and_periods.json').write_text(json.dumps(checks,indent=2))
lines=['# EURUSD frozen-model tick results — 30 September 2026','',
 'TRAIN/VALIDATION only. OOS untouched. No parameter optimization. All scenarios retained. These remain model-based historical results; broker commission, swap and exact fill latency are unverified.','',
 '| Model | Split | Cost scenario | Trades | Mean R | PF | Win % | Max DD R | Worst R | Mean duration h |',
 '|---|---|---|---:|---:|---:|---:|---:|---:|---:|']
for r in data['results']:
 lines.append(f'| {r["model"]} | {r["split"]} | {r["scenario"]} | {r["trades"]} | {r["expectancy_R"]:.4f} | {r["PF"]:.3f} | {100*r["win_rate"]:.1f} | {r["max_DD_R"]:.2f} | {r["worst_R"]:.3f} | {r["average_duration_hours"]:.2f} |')
lines.extend(['','## Cost scenarios','',
 'Observed quotes: historical Bid/Ask, one point adverse market/stop slippage, hypothetical USD 1 round-trip commission per standard EURUSD lot. Stress 1.5: 1.5x historical spread, two points slippage, hypothetical USD 7 commission. Stress 2: 2x spread, three points slippage, hypothetical USD 7 commission. Actual tariff unknown; these labels do not claim normal broker fees. Swap omitted. TP assumes ideal resting limit at requested price, without favorable gap improvement; real fill priority is unverified.','',
 'Entry/SL/TP use the original formulas, now anchored to actual entry quotes. Sequential eligibility follows actual exit time. Thus the trade population may differ from the earlier candle engine. No loss trades were removed to reconcile performance. Split boundaries use explicitly logged administrative flattening.','',
 'All trades pass closed-signal timing, non-overlap and initial SL/TP geometry checks. Monthly/yearly aggregates and direction counts are saved in Claude_sequential_tick_sanity_and_periods.json. Block-bootstrap intervals in the result JSON are exploratory 20-trade-block intervals, not multiplicity-adjusted proof.',''])
for model in data['protocol']['models']:
 normal=[r for r in data['results'] if r['model']==model and r['scenario']=='observed_quotes']
 supported=all(r['expectancy_R']>0 and r['PF']>1 for r in normal)
 lines.append(f'- {model}: '+('Further investigation only; costs/execution robustness unresolved.' if supported else 'No replicated positive expectancy in this frozen tick model; not an EA candidate.'))
lines.extend(['','These models are not the CRT + Supply/Demand hypothesis. Failure here neither establishes that EURUSD has no edge nor tests that discretionary methodology. No EA or live/demo deployment occurred.'])
(OUT/'Claude_SEQUENTIAL_TICK_RESULTS.md').write_text('\n'.join(lines),encoding='utf-8')
print('REPORT SAVED; all',len(checks),'scenario sequences passed consistency checks')
