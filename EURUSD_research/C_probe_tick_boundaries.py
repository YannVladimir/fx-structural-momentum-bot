"""Overlapping retrieval checks for first five chronological discrepancies."""
import json
from pathlib import Path
from datetime import datetime,timezone,timedelta
import numpy as np
import MetaTrader5 as m
ROOT=Path(__file__).resolve().parents[1]; OUT=Path(__file__).resolve().parent
rows=json.loads((OUT/'Claude_boundary_investigation.json').read_text())['rows'][:5]
results=[]
assert m.initialize(timeout=15000),m.last_error()
try:
 for row in rows:
  hour=datetime.fromisoformat(row['hour_utc']); boundary=hour+timedelta(hours=1)
  a=m.copy_ticks_range('EURUSD',boundary-timedelta(seconds=10),boundary+timedelta(seconds=10),m.COPY_TICKS_ALL)
  rec={'hour_utc':row['hour_utc']}
  if a is None or not len(a): rec['error']=str(m.last_error())
  else:
   day=hour.strftime('%Y-%m-%d')
   np.save(OUT/('Claude_boundary_probe_'+day+'.npy'),a)
   cutoff=int(boundary.timestamp()*1000)
   before=a[a['time_msc']<cutoff]
   rec.update(overlap_ticks=len(a),preboundary_ticks=len(before))
   if len(before):
    rec.update(overlap_last_msc=int(before['time_msc'][-1]),overlap_last_bid=float(before['bid'][-1]),
     archive_last_msc=row['last_tick_time_msc'],archive_last_bid=row['last_tick_bid'],
     overlap_finds_later_tick=bool(before['time_msc'][-1]>row['last_tick_time_msc']),
     reference_close_matches_overlap=bool(abs(float(before['bid'][-1])-row['reference_close'])<1e-9))
  results.append(rec); print(rec,flush=True)
finally: m.shutdown()
(OUT/'Claude_boundary_probe_results.json').write_text(json.dumps(results,indent=2))
