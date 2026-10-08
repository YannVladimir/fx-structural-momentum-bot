# EURUSD CRT + Supply/Demand — specification audit draft

30 September 2026. Specification only: no new CRT/Supply-Demand test run. The previous three independent EURUSD models are preserved. Earlier synthetic-index findings are preserved, including S/D INCONCLUSIVE due to insufficient sample. None of those conclusions is evidence for this new EURUSD hypothesis.

## Unchanged definitions recovered from source

Primary: H1 CRT, H4 zones/bias, M5 eventual entry refinement. Secondary: H4 CRT, D1 zones/bias, M15 eventual entry refinement. Lower-timeframe entry is not defined or tested in this round.

C1/C2 are consecutive completed CRT bars. Body = abs(C2.close-C2.open); exact zero rejects. Bullish: C2.low < C1.low, C2.high <= C1.high, min(C2.open,C2.close)-C2.low >= 2*body, and C1.low <= C2.close <= C1.high. Bearish: C2.high > C1.high, C2.low >= C1.low, C2.high-max(C2.open,C2.close) >= 2*body, and the same inclusive inside close. No color or C1-size filter. Both-side sweeps reject.

Bull target C1.high, invalidation C2.low; bear target C1.low, invalidation C2.high. Observe immediate C3 only. No entry, fixed-R target, position sizing or profitability inference is fabricated for this structural stage.

Demand base j: close[j] < open[j], high[j] > low[j]; zone [low[j],open[j]]. Archived source displacement is close[j+3]-close[j] >= 2*(high[j]-low[j]). Supply mirrors: close[j] > open[j], zone [open[j],high[j]], close[j]-close[j+3] >= 2*base_range. All three subsequent HTF bars must close before the zone exists. This is terminal close-to-close displacement, NOT maximum high/low reached during the three bars. This formula is retained from the approved v2 source; no extra base/displacement candle-color conditions are added.

Bull C2 lower wick intersects Demand iff C2.low <= zone.high and zone.low <= min(C2.open,C2.close). Bear C2 upper wick intersects Supply iff max(C2.open,C2.close) <= zone.high and zone.low <= C2.high. Touch is inclusive; no penetration threshold or requirement to close inside the zone. Zero prior CRT-timeframe touches; M5/M15 not used for freshness.

K=2 HTF bias remains the existing unique five-bar swing-confirmation state machine, sticky until the opposite confirmed swing level is broken by a closed HTF bar. Bias lookup uses latest HTF close time <= C2 close and is frozen through C3. UNDEFINED/opposing bias excludes only B2, never B1. This is the tested mathematical detector, not a claim that it captures the user's visual direction assessment.

## Concrete source conflicts and proposed dispositions

1. Freshness: `Claude_sd_zones.py:compute_first_overlap` uses searchsorted(...,side='right') on CRT OPEN timestamps. It skips the bar opening exactly at zone confirmation. Example zone confirmed 08:00, H1 bar 08:00–09:00 touches, C2 09:00–10:00: code can incorrectly retain the zone. Proposed correction: inspect CRT bars opening AT OR AFTER confirmation and fully closed before the candidate C2; include 08:00–09:00 in this example. C2 may be the first touch. No new threshold.

2. Zone availability: existing `zone_available_for_c2` permits zone_confirmed_at <= C2.close. Thus a zone confirmed at C2.close may be associated with a wick formed before the zone was knowable. This is available for prediction of C3 but does not prove an already-existing zone caused the rejection. User choice required: zone must be confirmed by C2.open (recommended for pre-existing location), OR retain confirmation by C2.close and explicitly label it retrospective location classification. Do not silently substitute one population for the other. A tick-specific confirmation-before-touch alternative adds complexity and is not proposed in this round.

3. C3 expiry: `Claude_crt_detector_v5.py` uses next available bar open as C3 end. That can span a weekend. Proposed correction: C3 ends at C3.open + 1h/4h, independent of the next available candle. A missing C3 or missing intrabar data is flagged, never extended or interpolated. Existing reports are not rewritten.

4. Legacy v2 document still labels itself pending approval despite subsequent user approval; its no-lookahead table incorrectly says zone-timeframe freshness. The human approval and later CRT-timeframe freshness correction govern. Source files and archived results remain unchanged; new versioned files will document any approved corrections.

5. Split leakage protection: the old builder assigns split by C2 open and then evaluates C3, potentially crossing a split boundary. Require C2 decision and the entire fixed C3 window to lie inside the relevant frozen split. Boundary-censored setups are separately counted, not shifted into another period or omitted based on outcome. This is a research containment control, not a trading alpha filter.

## Predeclared comparisons, conditional on resolving the timing choices

| Instrument | Structure | Comparison |
|---|---|---|
| EURUSD | Primary H1/H4 | Corrected CRT alone -> B1 (CRT + fresh zone location) |
| EURUSD | Primary H1/H4 | B1 -> B2 (same B1 + HTF alignment) |
| EURUSD | Secondary H4/D1 | Corrected CRT alone -> B1 |
| EURUSD | Secondary H4/D1 | B1 -> B2 |

B1/B2 are downstream subsets of identical corrected CRT setups, never redetection. TRAIN/VALIDATION boundaries remain exactly Claude_split_boundaries_EURUSD.json. OOS is not evaluated. Keep conservative alpha 0.00625; do not increase it because there are fewer EURUSD comparisons. Bull/bear diagnostic views are not separately declared significant.

For each comparison: random same-size subsets preserve direction and ratio/scale composition; 2,000 draws; geometry uses pre-C3 C2 close as the archived reference price, directional distances to C1 target/C2 invalidation, ratio and invalidation_distance/C1_range. Report matched support, effect in percentage points, relative effect, raw permutation p, both splits, bull/bear diagnostics, target/invalidation/neither rates, distributions and sample counts. No silent relaxation of geometry/scale matching. Sparse strata are reported as an inference limitation. Keep prior minimum review N=30 in both splits, stronger positive classification requiring TRAIN N>=100 plus positive significant replication at fixed alpha in both splits. Descriptive outcomes remain available when N is insufficient.

For structural path classification use chronological tick Bid level crossings consistently with Bid candle geometry, with millisecond order retained. This is theoretical structure, not executable long/short fills or R expectancy. Report simultaneous/same-timestamp ambiguities rather than invent order. Any subsequent executable strategy must use long Ask entry/Bid exit and short Bid entry/Ask exit, actual crossing fills, cost stress and the independently checked engine. Structural target-first results alone never qualify an EA.

## Open later-stage definitions

Meaningful C3 retracement and exact LTF Supply/Demand entry remain unfrozen. Do not interpret mere membership in C2 range as a retracement. No entry code, economic backtest or EA may be written from this draft until those later decisions are made and structural evidence warrants further work.

## Decision requested now

Confirm the freshness equality correction and fixed C3 expiry, and choose whether zone confirmation is required by C2 OPEN or by C2 CLOSE. Once decided, record a frozen EURUSD version before running these structural comparisons. No profitability-based selection or retuning.
