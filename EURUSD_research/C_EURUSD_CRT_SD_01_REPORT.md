# EURUSD CRT + Supply/Demand structural results — 30 September 2026

All four comparisons are INCONCLUSIVE due to insufficient retained sample, particularly VALIDATION. No entry strategy, R expectancy, account growth or EA performance was calculated. OOS remains untouched.

B1 = corrected CRT + fresh HTF location. B2 = the same B1 setups + closed-bar HTF direction. Zones must be confirmed by C2 open.

| Structure | Split | CRT N | B1 N (bull/bear) | Target first | Invalidation first | Neither | Matched null | Effect pp | Relative effect | Raw p |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Primary | TRAIN | 2375 | 30 (14/16) | 16.7% | 40.0% | 43.3% | 26.3% | -9.67 | -36.7% | 0.2669 |
| Primary | VALIDATION | 661 | 11 (6/5) | 36.4% | 18.2% | 45.5% | 29.9% | +6.41 | +21.4% | 0.7261 |
| Secondary | TRAIN | 580 | 3 (1/2) | 0.0% | 33.3% | 66.7% | 21.4% | -21.40 | -100.0% | 0.5812 |
| Secondary | VALIDATION | 161 | 2 (0/2) | 0.0% | 50.0% | 50.0% | 39.9% | -39.90 | -100.0% | 0.4973 |

Percentages with N<30 are descriptive, not affirmative statistical evidence. Alpha remains 0.00625; adjusted p=min(1,8p) is recorded in JSON. These figures do not establish economic expectancy.

## Incremental HTF direction

| Structure | Split | B2 N (bull/bear) | Target first | Matched B1 null | Effect pp | Raw p |
|---|---|---:|---:|---:|---:|---:|
| Primary | TRAIN | 11 (7/4) | 9.1% | 15.3% | -6.25 | 0.6672 |
| Primary | VALIDATION | 7 (4/3) | 28.6% | 30.8% | -2.21 | 1.0000 |
| Secondary | TRAIN | 2 (1/1) | 0.0% | 0.0% | +0.00 | 1.0000 |
| Secondary | VALIDATION | 0 (0/0) | — | — | — | — |

Every B2 cell is too small for meaningful inference. All nonempty B2 matched strata are sparse; repeated draws from tiny pools do not create new independent evidence.

## Direction diagnostics

| Structure | Split | B1 bullish N / target first | B1 bearish N / target first |
|---|---|---|---|
| Primary | TRAIN | 14 / 14.3% | 16 / 18.8% |
| Primary | VALIDATION | 6 / 33.3% | 5 / 40.0% |
| Secondary | TRAIN | 1 / 0.0% | 2 / 0.0% |
| Secondary | VALIDATION | 0 / — | 2 / 0.0% |

These direction views are diagnostic only, not separately declared significant.

## Distance geometry (B1 medians)

| Structure | Split | Target pips | Invalidation pips | Target/invalidation ratio | Invalidation/C1 range |
|---|---|---:|---:|---:|---:|
| Primary | TRAIN | 13.10 | 12.65 | 1.228 | 0.601 |
| Primary | VALIDATION | 10.40 | 7.80 | 1.368 | 0.552 |
| Secondary | TRAIN | 27.00 | 15.50 | 1.742 | 0.445 |
| Secondary | VALIDATION | 28.00 | 24.30 | 1.203 | 0.715 |

## Zones, timing and coverage

- Primary: 528 zones created in available history. By TRAIN end, 415/425 confirmed zones were consumed; by VALIDATION end, 508/528. Flags: {'MISSING_IMMEDIATE_C3': 18}.
  B1: INCONCLUSIVE (sample/coverage). B2: INCONCLUSIVE (sample/coverage).
- Secondary: 95 zones created in available history. By TRAIN end, 67/76 confirmed zones were consumed; by VALIDATION end, 82/95. Flags: {'MISSING_IMMEDIATE_C3': 12}.
  B1: INCONCLUSIVE (sample/coverage). B2: INCONCLUSIVE (sample/coverage).

Zones-consumed figures count first return by the stated endpoint, not a hypothetical count of profitable trades. Zone availability for every C2 explicitly requires prior confirmation and zero earlier CRT-bar touches. Warm-up uses available HTF history starting November 2022; older pre-period zones are unknown.

No retained setup had missing C3 ticks or equal-millisecond opposite crossing ambiguity. Boundary-censored and missing-immediate-C3 setups are flagged rather than extended or silently merged across splits. Prior no-OOS claims for this new run apply to the fixed bounded datasets; archived old runs remain unchanged.

Seven timing tests passed. The underlying corrected daily tick dataset already reconciles exactly to all 19,818 H1 reference bars. That consistency does not guarantee broker stop/limit fills. Structural outcome classification uses Bid to match Bid candle geometry and does not simulate a position. Future executable research would require the independently checked Bid/Ask engine, actual entry rules and verified costs.

Sample-sparsity controls: Primary B1 matching pools have no <20-observation strata; Secondary VALIDATION B1 has two sparse strata (6 and 16 parent observations). Every nonempty B2 comparison has sparse parent strata. No matching rules were relaxed or direction-only fallback used.

Preserve the frozen rules. The modest Primary validation improvement is based on 11 setups and reverses the TRAIN effect; it is not a promising result. Secondary has only five B1 observations overall. No claim of profitability, failure of the entire discretionary method, or readiness for EA implementation is justified. Stop here; no OOS or automatic LTF refinement.