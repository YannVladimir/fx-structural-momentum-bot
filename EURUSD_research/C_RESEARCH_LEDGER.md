# EURUSD research ledger — 30 September 2026

## Preserved experiments

1. Three fixed H1 candle screens: negative in TRAIN/VALIDATION under the originally assumed costs. Retained as preliminary due to unverified spread fallback.
2. Four price-only conditions at three fixed horizons: gross directional diagnostics did not identify a robust replicated candidate. These were not executable strategies.
3. Historical data audit: recovered continuous ticks; found omitted end-of-day ticks; version 02 repaired 642 ticks. All 19,818 pre-OOS reference H1 candles reconcile exactly. Original defective archives retained.
4. Independent execution model: nine deterministic mechanics tests passed; six chronological pilot replays resolved. No inference from selected pilot profitability.
5. Full sequential tick revalidation: the same three fixed H1 models, two chronological splits and three declared cost scenarios, 18 results. Every observed-quote model is negative in both splits. All stress runs are also negative. All sequences pass timing/non-overlap/geometry checks. Full trade files and monthly/yearly results retained. No unresolved trades or losses removed.

## Decision

No EA candidate is supported among these three independently proposed models under the tested assumptions. This is not proof that every EURUSD strategy fails. Swap and actual account commission remain unverified; no live evidence exists. Neither changing directions nor optimizing the parameters to reverse the result is justified by this study.

The next track, as the user requested, is their CRT + Supply/Demand methodology as a separate EURUSD hypothesis. Its approved historical specification must be audited and carried forward explicitly before coding: no silent repair of discrepancies in the earlier draft, no new conditions or optimized thresholds, and no reinterpretation of closed synthetic-index results. The original document still labels itself pending approval even though the user subsequently approved it; the user messages and recorded freshness correction govern. The remaining entry/retracement definitions must not be invented.

OOS has not been evaluated in any of the current EURUSD independent screens/replays. No EA or demo/live orders were placed. A 20% account drawdown ceiling is a user limit, not demonstrated protection or recommended sizing.
