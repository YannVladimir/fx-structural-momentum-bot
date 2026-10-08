# EURUSD preliminary screening — 30 September 2026

No deployable candidate identified in this initial screen. This does not establish that EURUSD has no edge.

The saved H1 data contains 19,818 bars inside the previously frozen TRAIN/VALIDATION boundaries. No duplicate timestamps or invalid OHLC relationships were found in that subset. Calendar/session continuity, broker-feed comparability and tick coverage have not been validated. Reserved OOS rows were excluded before indicator and outcome calculations. No OOS outcomes were evaluated.

Three fixed hypotheses were recorded before running: 12-bar directional momentum, close beyond the preceding 20-bar range, and one-sided failed breakout of that range. Both directions were enabled. Stops used 1.5 times SMA true range over 14 bars; targets used twice initial distance; time exits used at most 24 H1 bars. These are new exploratory models, not the previously frozen CRT or synthetic-index strategy. No parameter optimization occurred.

| Model | TRAIN trades | TRAIN mean R | TRAIN PF | VALIDATION trades | VALIDATION mean R | VALIDATION PF |
|---|---:|---:|---:|---:|---:|---:|
| Momentum 12 | 1,344 | -0.0623 | 0.902 | 341 | -0.0437 | 0.931 |
| Range breakout 20 | 730 | -0.0936 | 0.859 | 190 | -0.0957 | 0.852 |
| Failed breakout 20 | 835 | -0.0849 | 0.870 | 225 | -0.0870 | 0.862 |

All remained negative under 1.5x and 2x spread stress. None qualifies for implementation. No assertion of statistical significance is made from these exploratory comparisons.

Costs use recorded bar spreads, a fallback of 11 points for missing/zero spread, adverse slippage per fill, and a hypothetical commission allowance of USD 1 per 100,000 currency units round trip. Commission is not a verified broker tariff; swap is omitted. Stop-first is assumed if both barriers are inside one bar; opening gaps fill at the worse opening quote. Intrabar jump overshoot, historical quote updates, tick ordering, exact exit duration and future broker execution are unresolved. These results are OHLC screening results only, not execution validation.

Block-bootstrap expectancy intervals use circular blocks of 20 consecutive trades and 2,000 draws, as descriptive uncertainty estimates. Block length has not been established from dependence diagnostics.

Raw download is incomplete: M1/M5/M15/H1 files exist; H4/D1/tick outputs and completion manifest are absent. Recent M1/M5 history lies in reserved OOS and was not used to discover or select models. More pre-OOS intraday and tick coverage is needed before broader research or any bot acceptance.

The script, protocol, complete results and trade records are preserved beside this report. No EA was written, no live trading enabled, and previous closed research was not modified.
