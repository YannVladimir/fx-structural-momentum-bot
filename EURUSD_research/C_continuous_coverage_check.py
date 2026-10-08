"""Coverage and price reconciliation only; never compute strategy performance."""
import json
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; OUT=Path(__file__).resolve().parent
corrected='--corrected' in sys.argv
manifest=json.loads((OUT/('Claude_corrected_tick_manifest_02.json' if corrected else 'Claude_continuous_tick_manifest.json')).read_text())
if manifest['status'] not in ('acquisition_complete_coverage_not_yet_validated','repair_complete_reconciliation_required'):
 raise RuntimeError('Acquisition is not complete: '+manifest['status'])
bars=np.load(ROOT/'raw_data/Claude_EURUSD_20260930/H1.npy')
lookup={int(b['time']):b for b in bars}
total=compared=bad=0; max_error=0.; examples=[]; tick_times=set(); m1=m5=0
for day,rec in sorted(manifest['days'].items()):
 if rec['status']!='saved': continue
 with np.load(ROOT/'raw_data'/('Claude_EURUSD_preOOS_ticks_02' if corrected else 'Claude_EURUSD_preOOS_ticks')/(day+'.npz')) as data:
  total+=rec['rows']; m1+=len(data['M1']); m5+=len(data['M5'])
  for b in data['H1']:
   t=int(b['time']); tick_times.add(t)
   if t not in lookup: continue
   ref=lookup[t]; error=max(abs(float(b[k])-float(ref[k]))/1e-5 for k in ['open','high','low','close'])
   compared+=1; max_error=max(max_error,error)
   if error>1.000001:
    bad+=1
    if len(examples)<20: examples.append({'timestamp_utc_epoch':t,'maximum_error_points':error})
from datetime import datetime,timezone
def epoch(s): return int(datetime.fromisoformat(s).timestamp())
start=epoch(manifest['start_utc']); end=epoch(manifest['end_exclusive_utc'])
expected={int(b['time']) for b in bars if start<=int(b['time']) and int(b['time'])+3600<=end}
no_ticks=[{'date':day,**r} for day,r in manifest['days'].items() if r['status']=='no_ticks_returned']
report={'OOS_evaluated':False,'downloaded_ticks':total,'compressed_bytes':sum(r.get('bytes',0) for r in manifest['days'].values()),
 'M1_bars':m1,'M5_bars':m5,'H1_compared':compared,'H1_errors_above_one_point':bad,'max_H1_error_points':max_error,
 'mismatch_examples':examples,'expected_H1_without_ticks':sorted(expected-tick_times),
 'tick_H1_without_reference':sorted(tick_times-set(lookup)),
 'no_tick_days':no_ticks,'note':'Missing ticks or matching candles do not by themselves establish tradable quotes, commission, fill certainty, or complete exchange-session coverage.'}
(OUT/('Claude_corrected_coverage_report_02.json' if corrected else 'Claude_continuous_coverage_report.json')).write_text(json.dumps(report,indent=2))
print({k:v for k,v in report.items() if k not in ['mismatch_examples','no_tick_days','expected_H1_without_ticks','tick_H1_without_reference']},flush=True)
print('missing_H1',len(report['expected_H1_without_ticks']),'no_tick_days',len(no_ticks),flush=True)
