"""Independent quote-trigger execution model, not a broker fill guarantee.

Market entry: first available quote at/after requested time, ask for buys and
bid for sells. Resting stops: first observed crossing closeout quote with
adverse slippage. TP: ideal resting limit at the requested level, without
favorable gap improvement. Missing ticks/latency/queue priority remain risks.
"""
from datetime import datetime,timezone,timedelta
from pathlib import Path
import numpy as np

class ReplayError(Exception): pass

def replay(chunks, entry_time_msc, deadline_msc, direction, stop, target,
           slippage_price=0., commission_price=0.):
    if direction not in (-1,1) or deadline_msc<=entry_time_msc:
        raise ReplayError('Invalid direction/time window')
    if slippage_price<0 or commission_price<0:
        raise ReplayError('Negative execution costs')
    entry=None; entry_tick=None; previous=None; last_seen=None
    best=float('-inf'); worst=float('inf')
    for ticks in chunks:
        if not len(ticks): continue
        if np.any(np.diff(ticks['time_msc'])<0) or (previous is not None and ticks['time_msc'][0]<previous):
            raise ReplayError('Tick chunks out of order')
        previous=int(ticks['time_msc'][-1])
        if np.any((ticks['bid']<=0)|(ticks['ask']<ticks['bid'])):
            raise ReplayError('Invalid quote')
        q=ticks[ticks['time_msc']>=entry_time_msc]
        if not len(q): continue
        if entry is None:
            first=q[0]
            if first['time_msc']>=deadline_msc: raise ReplayError('No entry quote within window')
            entry=float(first['ask'] if direction==1 else first['bid'])+direction*slippage_price
            entry_tick=int(first['time_msc'])
            if not (direction*(entry-stop)>0 and direction*(target-entry)>0):
                raise ReplayError('Actual entry outside requested stop/target geometry')
        close=q['bid'] if direction==1 else q['ask']
        stop_hit=(close<=stop) if direction==1 else (close>=stop)
        target_hit=(close>=target) if direction==1 else (close<=target)
        expired=q['time_msc']>=deadline_msc
        events=np.flatnonzero(stop_hit|target_hit|expired)
        last_seen=int(q['time_msc'][-1])
        if not len(events):
            excursion=direction*(close-entry)
            best=max(best,float(excursion.max())); worst=min(worst,float(excursion.min()))
            continue
        k=int(events[0]); quote=float(close[k]); tick=int(q['time_msc'][k])
        excursion=direction*(close[:k+1]-entry)
        best=max(best,float(excursion.max())); worst=min(worst,float(excursion.min()))
        # Resting orders precede time-based market closure at the same quote.
        if stop_hit[k]: reason='stop'; fill=quote-direction*slippage_price
        elif target_hit[k]: reason='target'; fill=float(target)
        else: reason='time'; fill=quote-direction*slippage_price
        risk=direction*(entry-stop)
        return {'entry_time_msc':entry_tick,'exit_time_msc':tick,'direction':direction,'entry':entry,
                'stop':float(stop),'target':float(target),'exit':fill,'exit_quote':quote,'reason':reason,
                'initial_risk_price':risk,'R':(direction*(fill-entry)-commission_price)/risk,
                'entry_delay_msc':entry_tick-entry_time_msc,'MFE_R':max(0.,best/risk),'MAE_R':max(0.,-worst/risk),
                'exit_spread_price':float(q['ask'][k]-q['bid'][k]),
                'stop_overshoot_price':max(0.,direction*(stop-quote)) if reason=='stop' else 0.}
    raise ReplayError(f'Unresolved trade: insufficient subsequent quotes; last_seen={last_seen}')

def daily_chunks(folder, start_msc, end_exclusive_msc):
    """Only source files inside this bound; missing files must match manifest status."""
    import json
    folder=Path(folder)
    if folder.name!='Claude_EURUSD_preOOS_ticks_02':
        raise ReplayError('Original archive has known boundary omissions; use reconciled version 02')
    manifest=json.loads((folder.parents[1]/'EURUSD_research/Claude_corrected_tick_manifest_02.json').read_text())
    report_path=folder.parents[1]/'EURUSD_research/Claude_corrected_coverage_report_02.json'
    if not report_path.exists(): raise ReplayError('Corrected coverage audit not available')
    coverage=json.loads(report_path.read_text())
    if coverage['expected_H1_without_ticks'] or coverage['H1_errors_above_one_point']:
        raise ReplayError('Corrected price reconciliation has unresolved material discrepancies')
    cutoff=int(datetime.fromisoformat(manifest['end_exclusive_utc']).timestamp()*1000)
    if end_exclusive_msc>cutoff: raise ReplayError('Attempt to read reserved OOS quotes')
    day=datetime.fromtimestamp(start_msc/1000,timezone.utc).replace(hour=0,minute=0,second=0,microsecond=0)
    while int(day.timestamp()*1000)<end_exclusive_msc:
        key=day.strftime('%Y-%m-%d'); path=folder/(key+'.npz')
        if not path.exists():
            if manifest['days'].get(key,{}).get('status')!='no_ticks_returned':
                raise ReplayError('Missing unclassified tick file '+key)
        else:
            with np.load(path) as z:
                q=z['ticks']; yield q[(q['time_msc']>=start_msc)&(q['time_msc']<end_exclusive_msc)]
        day+=timedelta(days=1)
