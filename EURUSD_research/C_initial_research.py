"""Preliminary OHLC screening only. Existing OOS is never evaluated."""
import json
from pathlib import Path
from datetime import datetime, timezone
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'EURUSD_research'
BOUND = json.loads((ROOT/'CRT_research/data/Claude_split_boundaries_EURUSD.json').read_text())
def ts(s):
    return int(datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp())

CONFIG = {
    'status': 'PRELIMINARY OHLC SCREEN; NOT EXECUTION VALIDATED',
    'splits': BOUND,
    'models': ['momentum_12', 'range_breakout_20', 'failed_breakout_20'],
    'stop': 'SMA true range 14 * 1.5, calculated at signal close',
    'target': '2 initial stop distances',
    'entry': 'next H1 open; long ask, short bid',
    'exit': 'long bid / short ask; first opening gap then intrabar barriers; both touched means stop first',
    'holding_limit': '24 H1 bars, or last available bar before split end',
    'costs': 'historical bar spread; zero/missing spread replaced by 11 points; 1 USD per 100k currency units round-trip commission allowance',
    'stress': '1x spread + 1 point per fill; 1.5x + 2; 2x + 3',
    'constraints': 'one position, no averaging, no sizing changes, no optimization; gaps filled at worse opening quote',
    'limitations': 'OHLC cannot reveal true stop blow-through, changing intrabar spread, or tick order; no economic validation claimed',
}
(OUT/'Claude_screen_protocol.json').write_text(json.dumps(CONFIG,indent=2))
# Protocol saved before outcome calculations.
a = np.load(ROOT/'raw_data/Claude_EURUSD_20260930/H1.npy')
# Remove reserved OOS before any indicators/outcome computation.
a = a[(a['time'] >= ts(BOUND['train_start'])) & (a['time'] <= ts(BOUND['val_end']))]
o,h,l,c = (a[k].astype(float) for k in ['open','high','low','close'])
tr=np.maximum(h-l,np.maximum(abs(h-np.roll(c,1)),abs(l-np.roll(c,1))))
tr[0]=h[0]-l[0]
atr=np.full(len(a),np.nan)
for i in range(13,len(a)): atr[i]=np.mean(tr[i-13:i+1])
signals={k:np.zeros(len(a),dtype=int) for k in CONFIG['models']}
for i in range(20,len(a)):
    hi=np.max(h[i-20:i]); lo=np.min(l[i-20:i])
    signals['momentum_12'][i]=int(np.sign(c[i]-c[i-12]))
    signals['range_breakout_20'][i]=1 if c[i]>hi else -1 if c[i]<lo else 0
    signals['failed_breakout_20'][i]=-1 if h[i]>hi and lo<=c[i]<=hi and l[i]>=lo else 1 if l[i]<lo and lo<=c[i]<=hi and h[i]<=hi else 0

def stats(rows):
    r=np.array([x['r'] for x in rows]); w=r[r>0]; loss=r[r<0]
    eq=np.r_[0,np.cumsum(r)]; dd=np.maximum.accumulate(eq)-eq
    streak=best=0
    for x in r:
        streak=streak+1 if x<0 else 0; best=max(best,streak)
    # Dependence-aware uncertainty: sample consecutive 20-trade blocks.
    rng=np.random.default_rng(20260930); means=[]
    if len(r)>=20:
        for _ in range(2000):
            starts=rng.integers(0,len(r),size=(len(r)+19)//20)
            sample=r[(starts[:,None]+np.arange(20))%len(r)].ravel()[:len(r)]
            means.append(float(np.mean(sample)))
    return {'trades':len(r),'win_rate':float(len(w)/len(r)) if len(r) else None,
        'expectancy_R':float(np.mean(r)) if len(r) else None,
        'profit_factor':float(w.sum()/(-loss.sum())) if len(loss) else None,
        'total_R':float(r.sum()),'max_drawdown_R':float(dd.max()),
        'average_win_R':float(w.mean()) if len(w) else None,
        'average_loss_R':float(loss.mean()) if len(loss) else None,
        'worst_R':float(r.min()) if len(r) else None,'max_consecutive_losses':best,
        'block_bootstrap_mean_CI95':list(np.quantile(means,[.025,.975])) if means else None,
        'average_holding_hours':float(np.mean([x['hours'] for x in rows])) if rows else None}

results=[]
for split,start,end in [('TRAIN',BOUND['train_start'],BOUND['train_end']),('VALIDATION',BOUND['val_start'],BOUND['val_end'])]:
    eligible=np.where((a['time']>=ts(start))&(a['time']<=ts(end)))[0]
    for name,signal in signals.items():
        for mult,slip in [(1.,1),(1.5,2),(2.,3)]:
            trades=[]; i=int(eligible[0]); last=int(eligible[-1])
            while i<last:
                d=int(signal[i]); risk=float(atr[i]*1.5)
                if not d or not np.isfinite(risk) or risk<=0: i+=1; continue
                j=i+1
                spread=max(float(a[j]['spread']),11 if a[j]['spread']<=0 else 0)*1e-5*mult
                entry=o[j]+(spread if d==1 else 0)+d*slip*1e-5
                stop=entry-d*risk; target=entry+d*2*risk
                reason='time'; k=min(j+23,last); fill=None
                for z in range(j,min(j+23,last)+1):
                    spr=max(float(a[z]['spread']),11 if a[z]['spread']<=0 else 0)*1e-5*mult
                    offset=spr if d==-1 else 0
                    qo,qh,ql=o[z]+offset,h[z]+offset,l[z]+offset
                    if (qo-stop)*d<=0: fill=qo; reason='stop_gap'
                    elif (qo-target)*d>=0: fill=target; reason='target'
                    elif (ql<=stop if d==1 else qh>=stop): fill=stop; reason='stop'
                    elif (qh>=target if d==1 else ql<=target): fill=target; reason='target'
                    if fill is not None: k=z; break
                if fill is None:
                    spr=max(float(a[k]['spread']),11 if a[k]['spread']<=0 else 0)*1e-5*mult
                    fill=c[k]+(spr if d==-1 else 0)
                fill-=d*slip*1e-5
                r=(d*(fill-entry)-.00001)/risk
                trades.append({'entry_utc':int(a[j]['time']),'exit_bar_utc':int(a[k]['time']),
                    'direction':d,'entry':entry,'stop':stop,'target':target,'exit':fill,'reason':reason,'r':r,
                    'hours':float((a[k]['time']-a[j]['time'])/3600+1)})
                i=k+1
            record={'split':split,'model':name,'spread_multiplier':mult,'slippage_points_each_fill':slip,**stats(trades)}
            results.append(record)
            (OUT/f'Claude_trades_{split}_{name}_{mult}.json').write_text(json.dumps(trades,indent=2))
report={'protocol':CONFIG,'data_rows_train_validation':len(a),'duplicates':int(len(a)-len(np.unique(a['time']))),
    'invalid_ohlc':int(np.sum((h<np.maximum(o,c))|(l>np.minimum(o,c))|(h<l))),
    'results':results,'OOS_evaluated':False}
(OUT/'Claude_initial_screen_results.json').write_text(json.dumps(report,indent=2))
for x in results:
    print(x['split'],x['model'],x['spread_multiplier'],x['trades'],round(x['expectancy_R'],4) if x['expectancy_R'] is not None else None,x['profit_factor'],x['block_bootstrap_mean_CI95'])
