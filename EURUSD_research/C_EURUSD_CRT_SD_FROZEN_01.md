# EURUSD CRT + Supply/Demand — frozen structural experiment 01

Frozen on 30 September 2026, after explicit user approval of the timing corrections and zone confirmation before C2 opens. The prior draft's unchanged formulas and controls govern. No experiment results were inspected before this freeze.

Primary H1 CRT/H4 zone and bias; Secondary H4 CRT/D1 zone and bias. Corrected CRT geometry is unchanged: one-sided strict sweep, nonzero body, directional wick >=2*body, inclusive C2 close inside C1. No color, size, entry or other filters.

Supply/Demand retains approved v2 terminal close-to-close displacement: net move from base close to third following candle close >=2*base range. Base is single opposing candle; demand [base.low,base.open], supply [base.open,base.high]. No additional candle-sequence criterion is introduced. Zone exists only after the third following HTF candle closes. `confirmed_at <= C2.open` is required: a candle closing exactly at C2 open is fully available before C2 trades.

Freshness includes CRT candles opening AT zone confirmation. First CRT-range overlap consumes the zone; C2 may itself be that first overlap. A prior CRT candle's inclusive [low,high] intersection consumes it, irrespective of candle color. C2 directional rejection wick must intersect an eligible fresh zone. No LTF entry or freshness rules. No penetration depth.

C3 starts exactly at C2.open + CRT period and ends one period later. If the immediate next available bar does not start there, flag MISSING_IMMEDIATE_C3 rather than extend the window. C1/C2 remain consecutive completed available candles as previously defined. Entire C2 decision/C3 observation must fall within the same frozen split. Flag boundary-censored setups separately. No extension across weekends, no interpolation.

B1 = corrected CRT filtered only by fresh location. B2 = SAME B1 filtered by K=2 HTF alignment; latest fully closed HTF bar at C2.close, frozen through C3. Original swing algorithm unchanged. UNDEFINED/opposing excludes B2 only.

Four predeclared comparisons: Primary CRT->B1, Primary B1->B2, Secondary CRT->B1, Secondary B1->B2. Same conservative alpha 0.00625. 2,000 stratified replacement draws preserve bullish/bearish counts and coarse ratio/scale tertiles. Bucket boundaries follow earlier B1 runner (33.33/66.67 percentiles within direction and split). Labels remain identical when subsetting into B1/B2. No direction-only fallback or relaxed geometry. Strata with <20 parent observations are reported; all observations retained. Raw effects, relative effects and p-values reported. Diagnostics by direction are descriptive only. Minimum review N=30 in both splits; strongest positive classification requires TRAIN N>=100, positive effects and p<0.00625 in both splits. Any ambiguous tick order or degenerate matching geometry blocks affirmative classification rather than choosing favorable labels.

Distance geometry uses C2 close, the reference known before C3, to unchanged C1 target/C2 invalidation. Scale = invalidation distance/C1 range; ratio = target/invalidation distance. Both normalized distances reported. No data from C3 determines matching strata. Outcomes: TARGET_FIRST, INVALID_FIRST, NEITHER; any equal-millisecond opposite crossings flagged AMBIGUOUS and not silently resolved. Quote sequencing uses actual corrected tick Bid to match Bid candle geometry. This is structural prediction, not executable TP/SL fills, entry P&L or R expectancy.

Use existing EURUSD TRAIN 2022-11-01 to 2025-05-06 15:00 H1 bar (close 16:00); VALIDATION from 2025-05-06 16:00 to 2026-01-08 20:00 H1 bar (close 21:00). OOS starts 2026-01-08 21:00. Use fixed nominal HTF close timestamps, never forming-bar states. Load only bars fully closed by OOS start, and observe C3 ticks strictly before it. Late setups crossing boundaries are separately counted. Warm-up starts with available November 2022 H4/D1 history; older pre-period zones/bias are not inferred.

No OOS outcomes, Supply/Demand entry refinement, profit/account-growth calculation or EA. Do not change thresholds following results. Stop after structural report, preserving all cells and previous source/results unchanged.
