"""Fixed historical execution probes; no strategy or OOS outcomes."""
import json
from pathlib import Path
from datetime import datetime,timezone,timedelta
import numpy as np
import MetaTrader5 as m
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(__file__).resolve().parent
DATA=ROOT/'raw_data/Claude_EURUSD_20260930'
DATES=['2022-11-08','2023-06-06','2024-06-04','2025-06-03','2025-12-02']
def utc(s): return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)
report={'purpose':'cost and coverage only','OOS_evaluated':False,'probes':[],'intraday_requests':[]}
assert m.initialize(timeout=15000),m.last_error()
try:
 info=m.symbol_info('EURUSD'); report['maxbars']=m.terminal_info().maxbars
 account=m.account_info()
 report['account_cost_context']={'currency':account.currency,'leverage':account.leverage,'trade_mode':account.trade_mode} if account else None
 for date in DATES:
  start=utc(date+'T00:00:00'); end=start+timedelta(days=1)
  path=DATA/('ticks_day_'+date+'.npy')
  if path.exists(): ticks=np.load(path)
  else:
   ticks=m.copy_ticks_range('EURUSD',start,end-timedelta(milliseconds=1),m.COPY_TICKS_ALL)
   if ticks is not None and len(ticks): np.save(path,ticks)
  rec={'date_utc':date}
  if ticks is None or not len(ticks): rec['error']=str(m.last_error())
  else:
   valid=(ticks['bid']>0)&(ticks['ask']>=ticks['bid'])
   spread=(ticks['ask'][valid]-ticks['bid'][valid])/info.point
   gaps=np.diff(ticks['time_msc'])/1000
   rec.update(rows=len(ticks),invalid_quotes=int(np.sum(~valid)),equal_bid_ask_fraction=float(np.mean(spread==0)),
    spread_points_quantiles=np.quantile(spread,[.5,.9,.99,1]).tolist(),
    gap_seconds_quantiles=np.quantile(gaps,[.5,.99,1]).tolist(),backward_tick_times=int(np.sum(gaps<0)))
   rates=m.copy_rates_range('EURUSD',m.TIMEFRAME_H1,start,end-timedelta(seconds=1))
   hourly=[]
   if rates is not None:
    for bar in rates:
     z=ticks[(ticks['time']>=bar['time'])&(ticks['time']<bar['time']+3600)]
     if not len(z):
      hourly.append({'hour_utc':int(bar['time']),'tick_count':0}); continue
     sp=(z['ask']-z['bid'])/info.point
     hourly.append({'hour_utc':int(bar['time']),'tick_count':len(z),'bar_spread_points':int(bar['spread']),
      'tick_spread_median':float(np.median(sp)),'tick_spread_min':float(np.min(sp)),
      'bid_ohlc_error_points':[(float(v)-float(bar[k]))/info.point for k,v in zip(['open','high','low','close'],[z['bid'][0],z['bid'].max(),z['bid'].min(),z['bid'][-1]])]})
   rec['hourly_comparison']=hourly
  report['probes'].append(rec)
  print(date,{k:v for k,v in rec.items() if k!='hourly_comparison'},flush=True)
  (OUT/'Claude_cost_coverage_audit.json').write_text(json.dumps(report,indent=2))
  # Fixed monthly-range request; no changing history boundaries or MT5 settings.
  for tf in ['M1','M5']:
   rates=m.copy_rates_range('EURUSD',getattr(m,'TIMEFRAME_'+tf),start,end-timedelta(seconds=1))
   req={'date_utc':date,'timeframe':tf,'rows':0 if rates is None else len(rates)}
   if rates is None or not len(rates): req['error']=str(m.last_error())
   else:
    in_range=(rates['time']>=int(start.timestamp()))&(rates['time']<int(end.timestamp()))
    req['out_of_requested_range_rows']=int(np.sum(~in_range))
    req['usable_rows']=int(np.sum(in_range))
    if in_range.any(): np.save(DATA/(tf+'_probe_'+date+'.npy'),rates[in_range])
    else: req['error']='MT5 returned only out-of-range bars; not valid history'
   report['intraday_requests'].append(req)
   print('intraday',req,flush=True)
 # Only EURUSD cost fields from already-closed deals; no account IDs or credentials exported.
 deals=m.history_deals_get(utc('2022-11-01'),utc('2026-01-08T21:00:00'))
 relevant=[] if deals is None else [d for d in deals if d.symbol=='EURUSD' and d.volume>0]
 report['historical_deal_costs']={'EURUSD_deals':len(relevant),'commission_total':sum(d.commission for d in relevant),
  'fees_total':sum(d.fee for d in relevant),'swap_total':sum(d.swap for d in relevant),
  'note':'Zero or absent deal records do not establish zero tariff; intended account type still unconfirmed.'}
finally: m.shutdown()
(OUT/'Claude_cost_coverage_audit.json').write_text(json.dumps(report,indent=2))
print('COST COVERAGE AUDIT COMPLETE',flush=True)
