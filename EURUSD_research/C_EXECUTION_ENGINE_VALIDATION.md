# Tick replay technical validation — 30 September 2026

## Boundary retrieval bug

The initial daily downloads omitted some final-second ticks. Overlapping 20-second queries for five chronological discrepancies recovered later pre-midnight ticks, all reproducing the reference close. Version 02 then replaced the final ten seconds of each saved interval using exact endpoint requests followed by an explicit local half-open timestamp filter. Any returned endpoint quote was discarded; no OOS outcomes were evaluated.

The repair recovered 642 ticks, bringing the corrected archive to 88,405,612 ticks. Original archives and discrepancy reports remain unchanged. Corrected data occupies 626,280,568 bytes. All 19,818 reference H1 candles now match tick-reconstructed open, high, low and close exactly. There are no reference H1 bars missing from ticks. This validates candle price/time consistency for these intervals, not all quote executability or broker fills. Empty calendar dates remain documented; historical broker-session confirmation is unfinished.

## Independent execution rules

First available quote at or after the requested entry timestamp: buy at Ask, sell at Bid, with adverse market slippage. Long stops/targets trigger on Bid; short stops/targets trigger on Ask. A stop fills at the first observed crossing closeout quote plus adverse slippage; it can lose more than 1R. A TP uses an ideal resting-limit fill at the requested level, without favorable gap improvement. That is an explicit modeling assumption, not guaranteed fill priority. Time exit uses the first subsequent closeout quote; resting triggers at the same tick take precedence. Missing subsequent quotes produce an unresolved-trade error, never an invented price.

Risk denominator is actual entry-to-requested-stop distance. Monetary sizing and broker-specific volume/minimum-stop checks are not implemented in this research execution utility. Commission is supplied as an explicit equivalent price cost; real tariff is still unconfirmed. Swap, latency distributions, partial fills, queue priority and broker-specific trigger semantics require additional modeling before economic acceptance. Spread is embodied once by entry/closeout Bid/Ask quotes; no additional spread debit is added.

Nine deterministic tests passed: long gap stop, short gap stop, long TP, short Ask TP, delayed entry/time exit, adverse slippage and commission, absent exit quote, invalid/unordered quotes, and stop across chunks. These are implementation tests, not independent proof that the chosen execution assumptions describe the broker.

## Historical technical pilot

Six pilot trades were selected as the first chronological trade of each of the three earlier models in each split. Original requested SL/TP levels were retained, entry used actual quotes, and time limits retained the 24-H1-bar convention. No trade was selected for winning or losing. All six resolved without missing-data errors. Full results are in Claude_replay_smoke_results.json.

These pilot trades do not reproduce the complete live-sequential strategy population: actual exit timing can change later trade eligibility. No expectancy or PF verdict is inferred from them. One-point slippage and one-point hypothetical commission were technical test settings, not verified broker costs. The next economic comparison must regenerate the frozen signals with sequential eligibility driven by tick exits and report all candidates, costs and unresolved trades. No parameter retuning is authorized by the pilot.

The replay utility refuses the original uncorrected archive and requires version 02 reconciliation to pass. OOS remains untouched; no EA or deployment was performed. Previous preliminary outcome tables remain preserved and are not replaced by this technical audit.
