# EURUSD execution coverage findings — 30 September 2026

Five predeclared full UTC days were downloaded: 8 November 2022, 6 June 2023, 4 June 2024, 3 June 2025 and 2 December 2025. Total 455,346 ticks. No inverted/nonpositive quotes or backward millisecond timestamps in those samples. Reconstructed hourly bid OHLC matched retrieved MT5 H1 candles exactly for four days; maximum discrepancy on the fifth was one point. This supports price/time consistency for those samples only.

Typical tick-weighted median spreads were 1–2 points (0.1–0.2 pips), while maxima across sampled days ranged from 64 to 150 points (6.4–15 pips). Tick-weighted summaries are not time-weighted spreads or expected entry spreads. Equal Bid/Ask occurred frequently in some older samples, warranting broker/feed and commission validation; they do not establish zero executable trading costs.

MT5's 100,000-bar limit prevents reliable old intraday recovery through the current bar requests. Several requests returned a single June 2026 bar outside a requested 2022–2025 day. The original raw probe files are retained as evidence but marked unusable in Claude_cost_coverage_audit.json. The revised downloader now verifies request bounds before saving. No strategy calculation used those erroneous probe files.

Reconstructed M1 and M5 bid candles directly from actual tick sequences for all five sampled days. There are 1,440 M5 bars and 7,196 M1 bars across the samples. Four missing M1 clock buckets remain absent rather than being interpolated. Bid OHLC, tick counts, min/max spread, and first/last tick millisecond times are saved. Ask ticks remain available in the source files for executable replay. Sparse dates must never be concatenated as continuous strategy history.

No EURUSD deals were returned from the connected account over the research period. Commission/fee sums of zero over an empty sample do not establish zero commission. Account tariff, historical feed changes and overnight swap economics remain unresolved.

The initial screen's 11-point fallback for zero candle spreads remains an unverified cost assumption. Preserve that result as preliminary, and do not claim definitive strategy rejection or success until execution is independently modeled. No parameter retuning, OOS outcome evaluation, or EA deployment occurred.

Next gate: continuous TRAIN/VALIDATION tick-derived intraday coverage, session-aware coverage checks, verified commission assumptions and independent execution-engine checks. Then freeze any new strategy hypotheses before outcome testing. CRT + Supply/Demand remains a separate later track, not a rescue modification of earlier results.
