# EURUSD data audit — 30 September 2026

## Recovered data

Retrieved 5,125 H4 candles and 995 D1 candles for the existing research interval. These are raw bars; the last H4/D1 bars may extend beyond the reserved OOS start and must be excluded from any indicator lookup unless fully closed before the decision timestamp. Downloading bars is not permission to evaluate OOS outcomes.

Five fixed, 15-minute TRAIN/VALIDATION tick probes returned data on 8 November 2022, 6 June 2023, 4 June 2024, 3 June 2025 and 2 December 2025. No inverted/nonpositive Bid/Ask quotes occurred in these probes. This establishes sampled historical access only, not complete continuous tick coverage. All MT5 request datetimes were explicitly UTC-aware.

## Material cost uncertainty

Numerous candle spread fields are zero. A zero candle field must not automatically be interpreted as a tradable zero spread, nor automatically as missing data. Tick probes also contain equal Bid/Ask quotes. Historical quote construction/feed quality needs investigation. Median spreads in the five probes ranged from zero to two points; these short samples are not representative full-market cost estimates.

The initial three-model screen substituted 11 points whenever candle spread was zero. That assumption was not verified against historical ticks. It may bias results downward. Preserve its outputs as preliminary screening under that assumed cost scenario, not definitive model rejection or proof that EURUSD has no edge. Do not retune parameters in response.

Commission and swap cash charges remain unverified for the intended account. Current symbol properties are saved in Claude_data_audit.json; historical property constancy is not established.

## Coverage constraints

M1 has no downloaded pre-OOS rows. M5 starts 28 May 2025, after the frozen TRAIN end, so it cannot support a complete TRAIN/VALIDATION study. M15 reaches September 2022. H1 reaches August 2010, but historical feed consistency over that span is unverified.

Raw candle checks found no duplicate/nonincreasing timestamps or invalid OHLC relationships in the pre-OOS subsets. Time gaps were counted but include scheduled market closures; market-session/calendar-aware gap validation remains required. Prior frozen boundaries remain unchanged.

## Next research requirements

1. Establish actual account commission and intended trading/risk constraints.
2. Recover pre-OOS intraday coverage and validate trading-session gaps.
3. Compare candle spread fields with historical Bid/Ask ticks over broader pre-OOS periods.
4. Independently verify the initial engine and freeze a defensible execution model before new outcome comparisons.
5. Keep prior experiments unchanged, record all new hypotheses, and do not evaluate reserved OOS outcomes or deploy an EA during this audit.

No strategy parameters, closed CRT findings, or OOS results were changed.
