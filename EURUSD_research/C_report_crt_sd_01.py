"""Readable structural report and descriptive metadata; no new tests."""
import json
from pathlib import Path
from collections import Counter
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; OUT=Path(__file__).resolve().parent
data=json.loads((OUT/'Claude_CRT_SD_01_results.json').read_text())
lines=['# EURUSD CRT + Supply/Demand structural results — 30 September 2026','',
 'All four comparisons are INCONCLUSIVE due to insufficient retained sample, particularly VALIDATION. No entry strategy, R expectancy, account growth or EA performance was calculated. OOS remains untouched.','',
 'B1 = corrected CRT + fresh HTF location. B2 = the same B1 setups + closed-bar HTF direction. Zones must be confirmed by C2 open.','',
 '| Structure | Split | CRT N | B1 N (bull/bear) | Target first | Invalidation first | Neither | Matched null | Effect pp | Relative effect | Raw p |',
 '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for cell in data['cells']:
 for split in ['TRAIN','VALIDATION']:
  row=cell['splits'][split]; b=row['B1']; null=row['B1_vs_A1']
  lines.append(f'| {cell["structure"]} | {split} | {row["A1"]["N"]} | {b["N"]} ({b["bull"]}/{b["bear"]}) | {100*b.get("TARGET_FIRST_rate",0):.1f}% | {100*b.get("INVALID_FIRST_rate",0):.1f}% | {100*b.get("NEITHER_rate",0):.1f}% | {100*null["matched_null_rate"]:.1f}% | {100*null["effect_absolute"]:+.2f} | {100*null["effect_relative"]:+.1f}% | {null["p_value"]:.4f} |')
lines.extend(['','Percentages with N<30 are descriptive, not affirmative statistical evidence. Alpha remains 0.00625; adjusted p=min(1,8p) is recorded in JSON. These figures do not establish economic expectancy.','',
 '## Incremental HTF direction','',
 '| Structure | Split | B2 N (bull/bear) | Target first | Matched B1 null | Effect pp | Raw p |',
 '|---|---|---:|---:|---:|---:|---:|'])
for cell in data['cells']:
 for split in ['TRAIN','VALIDATION']:
  r=cell['splits'][split]; b=r['B2']; n=r['B2_vs_B1']
  if n is None:
   lines.append(f'| {cell["structure"]} | {split} | 0 (0/0) | — | — | — | — |')
  else:
   lines.append(f'| {cell["structure"]} | {split} | {b["N"]} ({b["bull"]}/{b["bear"]}) | {100*n["real_rate"]:.1f}% | {100*n["matched_null_rate"]:.1f}% | {100*n["effect_absolute"]:+.2f} | {n["p_value"]:.4f} |')
lines.extend(['','Every B2 cell is too small for meaningful inference. All nonempty B2 matched strata are sparse; repeated draws from tiny pools do not create new independent evidence.','',
 '## Direction diagnostics','',
 '| Structure | Split | B1 bullish N / target first | B1 bearish N / target first |',
 '|---|---|---|---|'])
for cell in data['cells']:
 for split in ['TRAIN','VALIDATION']:
  row=cell['splits'][split]; bull=row['B1_bull']; bear=row['B1_bear']
  bp=f'{100*bull["TARGET_FIRST_rate"]:.1f}%' if bull['N'] else '—'
  sp=f'{100*bear["TARGET_FIRST_rate"]:.1f}%' if bear['N'] else '—'
  lines.append(f'| {cell["structure"]} | {split} | {bull["N"]} / {bp} | {bear["N"]} / {sp} |')
lines.extend(['','These direction views are diagnostic only, not separately declared significant.','',
 '## Distance geometry (B1 medians)','',
 '| Structure | Split | Target pips | Invalidation pips | Target/invalidation ratio | Invalidation/C1 range |',
 '|---|---|---:|---:|---:|---:|'])
for cell in data['cells']:
 for split in ['TRAIN','VALIDATION']:
  r=cell['splits'][split]['B1']
  lines.append(f'| {cell["structure"]} | {split} | {r["target_distance_quantiles"][1]/1e-4:.2f} | {r["invalidation_distance_quantiles"][1]/1e-4:.2f} | {r["ratio_quantiles"][1]:.3f} | {r["scale_quantiles"][1]:.3f} |')
lines.extend(['','## Zones, timing and coverage',''])
metadata={}
for cell in data['cells']:
 label=cell['structure']; filename='H1.npy' if label=='Primary' else 'H4_preOOS.npy'
 bars=np.load(ROOT/'raw_data/Claude_EURUSD_20260930'/filename)
 observations=json.loads((OUT/f'Claude_CRT_SD_01_{label}_observations.json').read_text())
 # Metadata only, using C1 and at most its preceding 19 closed bars.
 for row in observations:
  i=int(np.searchsorted(bars['time'],row['c2_open'])); c1=bars[i-1]; c2=bars[i]
  assert row['HTF_close_used'] is None or row['HTF_close_used']<=row['C3_start']
  row['C1_range']=float(c1['high']-c1['low']); row['C2_range']=float(c2['high']-c2['low'])
  row['body_to_C2_range']=row['body']/row['C2_range']
  median=float(np.median(bars['high'][i-20:i]-bars['low'][i-20:i])) if i>=20 else None
  row['C1_range_to_rolling_median20_including_C1']=row['C1_range']/median if median and median>0 else None
 (OUT/f'Claude_CRT_SD_01_{label}_observations_with_metadata.json').write_text(json.dumps(observations,indent=2))
 flags=Counter(r['flag'] for r in cell['censored_or_missing_setups']); metadata[label]=dict(flags)
 train=cell['splits']['TRAIN']; val=cell['splits']['VALIDATION']
 lines.append(f'- {label}: {cell["zones_created"]} zones created in available history. By TRAIN end, {train["zones_consumed_by_split_end"]}/{train["zones_confirmed_by_split_end"]} confirmed zones were consumed; by VALIDATION end, {val["zones_consumed_by_split_end"]}/{val["zones_confirmed_by_split_end"]}. Flags: {dict(flags)}.')
 lines.append(f'  B1: {cell["B1_verdict"]}. B2: {cell["B2_verdict"]}.')
lines.extend(['',
 'Zones-consumed figures count first return by the stated endpoint, not a hypothetical count of profitable trades. Zone availability for every C2 explicitly requires prior confirmation and zero earlier CRT-bar touches. Warm-up uses available HTF history starting November 2022; older pre-period zones are unknown.','',
 'No retained setup had missing C3 ticks or equal-millisecond opposite crossing ambiguity. Boundary-censored and missing-immediate-C3 setups are flagged rather than extended or silently merged across splits. Prior no-OOS claims for this new run apply to the fixed bounded datasets; archived old runs remain unchanged.','',
 'Seven timing tests passed. The underlying corrected daily tick dataset already reconciles exactly to all 19,818 H1 reference bars. That consistency does not guarantee broker stop/limit fills. Structural outcome classification uses Bid to match Bid candle geometry and does not simulate a position. Future executable research would require the independently checked Bid/Ask engine, actual entry rules and verified costs.','',
 'Sample-sparsity controls: Primary B1 matching pools have no <20-observation strata; Secondary VALIDATION B1 has two sparse strata (6 and 16 parent observations). Every nonempty B2 comparison has sparse parent strata. No matching rules were relaxed or direction-only fallback used.','',
 'Preserve the frozen rules. The modest Primary validation improvement is based on 11 setups and reverses the TRAIN effect; it is not a promising result. Secondary has only five B1 observations overall. No claim of profitability, failure of the entire discretionary method, or readiness for EA implementation is justified. Stop here; no OOS or automatic LTF refinement.'])
(OUT/'Claude_EURUSD_CRT_SD_01_REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
print('STRUCTURAL REPORT SAVED',metadata)
