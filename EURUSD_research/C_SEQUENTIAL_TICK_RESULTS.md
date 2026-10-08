# EURUSD frozen-model tick results — 30 September 2026

TRAIN/VALIDATION only. OOS untouched. No parameter optimization. All scenarios retained. These remain model-based historical results; broker commission, swap and exact fill latency are unverified.

| Model | Split | Cost scenario | Trades | Mean R | PF | Win % | Max DD R | Worst R | Mean duration h |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| momentum_12 | TRAIN | observed_quotes | 1292 | -0.0448 | 0.930 | 36.1 | 73.90 | -2.075 | 15.06 |
| momentum_12 | TRAIN | stress_1_5 | 1319 | -0.0941 | 0.860 | 35.7 | 138.46 | -2.107 | 14.70 |
| momentum_12 | TRAIN | stress_2 | 1353 | -0.1608 | 0.774 | 33.6 | 230.19 | -2.993 | 14.23 |
| range_breakout_20 | TRAIN | observed_quotes | 724 | -0.0604 | 0.909 | 33.4 | 52.47 | -2.172 | 12.14 |
| range_breakout_20 | TRAIN | stress_1_5 | 735 | -0.1309 | 0.816 | 32.4 | 102.59 | -2.231 | 11.77 |
| range_breakout_20 | TRAIN | stress_2 | 744 | -0.1798 | 0.757 | 31.3 | 140.00 | -3.247 | 11.39 |
| failed_breakout_20 | TRAIN | observed_quotes | 817 | -0.0488 | 0.925 | 35.6 | 67.73 | -2.213 | 14.08 |
| failed_breakout_20 | TRAIN | stress_1_5 | 822 | -0.1165 | 0.830 | 34.4 | 112.90 | -2.786 | 13.81 |
| failed_breakout_20 | TRAIN | stress_2 | 840 | -0.1764 | 0.755 | 32.5 | 163.62 | -3.300 | 13.38 |
| momentum_12 | VALIDATION | observed_quotes | 346 | -0.0459 | 0.929 | 37.3 | 27.78 | -3.378 | 15.53 |
| momentum_12 | VALIDATION | stress_1_5 | 354 | -0.0798 | 0.881 | 36.7 | 38.79 | -3.420 | 15.01 |
| momentum_12 | VALIDATION | stress_2 | 361 | -0.1353 | 0.806 | 35.2 | 59.20 | -3.434 | 14.67 |
| range_breakout_20 | VALIDATION | observed_quotes | 188 | -0.0688 | 0.892 | 36.2 | 22.13 | -1.326 | 12.42 |
| range_breakout_20 | VALIDATION | stress_1_5 | 189 | -0.1545 | 0.775 | 34.4 | 37.09 | -1.609 | 11.53 |
| range_breakout_20 | VALIDATION | stress_2 | 194 | -0.1959 | 0.725 | 33.5 | 41.35 | -1.866 | 11.00 |
| failed_breakout_20 | VALIDATION | observed_quotes | 222 | -0.0789 | 0.876 | 34.7 | 35.05 | -1.333 | 14.64 |
| failed_breakout_20 | VALIDATION | stress_1_5 | 225 | -0.1807 | 0.738 | 32.4 | 54.29 | -1.693 | 14.16 |
| failed_breakout_20 | VALIDATION | stress_2 | 227 | -0.2102 | 0.705 | 32.2 | 58.87 | -2.120 | 13.77 |

## Cost scenarios

Observed quotes: historical Bid/Ask, one point adverse market/stop slippage, hypothetical USD 1 round-trip commission per standard EURUSD lot. Stress 1.5: 1.5x historical spread, two points slippage, hypothetical USD 7 commission. Stress 2: 2x spread, three points slippage, hypothetical USD 7 commission. Actual tariff unknown; these labels do not claim normal broker fees. Swap omitted. TP assumes ideal resting limit at requested price, without favorable gap improvement; real fill priority is unverified.

Entry/SL/TP use the original formulas, now anchored to actual entry quotes. Sequential eligibility follows actual exit time. Thus the trade population may differ from the earlier candle engine. No loss trades were removed to reconcile performance. Split boundaries use explicitly logged administrative flattening.

All trades pass closed-signal timing, non-overlap and initial SL/TP geometry checks. Monthly/yearly aggregates and direction counts are saved in Claude_sequential_tick_sanity_and_periods.json. Block-bootstrap intervals in the result JSON are exploratory 20-trade-block intervals, not multiplicity-adjusted proof.

- momentum_12: No replicated positive expectancy in this frozen tick model; not an EA candidate.
- range_breakout_20: No replicated positive expectancy in this frozen tick model; not an EA candidate.
- failed_breakout_20: No replicated positive expectancy in this frozen tick model; not an EA candidate.

These models are not the CRT + Supply/Demand hypothesis. Failure here neither establishes that EURUSD has no edge nor tests that discretionary methodology. No EA or live/demo deployment occurred.