# Continuous EURUSD recovery — 30 September 2026

Acquired 88,404,970 actual historical ticks from 1 November 2022 00:00 UTC up to, but excluding, 8 January 2026 21:00 UTC. These are the existing TRAIN/VALIDATION dates. Daily compressed archives include original Bid/Ask ticks and reconstructed bid M1, M5 and H1 candles. Storage totals 626,276,262 bytes, approximately 626 MB decimal. OOS data was not requested or evaluated by this job.

Reconstructed 1,186,546 M1 bars and 237,422 M5 bars without interpolation of empty clock buckets. Every retrieved tick passed requested-time-bound checks, monotonic millisecond ordering and positive/noninverted quote checks. Those checks do not establish that every historical tick is present or that every quote was executable.

All 19,818 reference H1 bars in the research interval have corresponding tick-derived hours; there are no additional tick-derived hours without a reference bar. Of these comparisons, 60 (approximately 0.30%) differ by more than one point in at least one OHLC component. Maximum discrepancy is 18 points (1.8 pips). The first 20 discrepancy examples all occur in the 23:00 UTC hour, suggesting a day-boundary/rollover issue, but the cause is not established. Do not silently discard these hours or select the feed that improves strategy results. Signal-versus-tick differences must be explicitly investigated before final research acceptance.

There are 170 calendar days with no ticks returned. Only one is a weekday: 26 December 2022. This is consistent with a possible holiday closure but has not been confirmed against the broker's historical trading schedule. Remaining empty days are weekend dates; weekend dates can also contain legitimate Sunday trading sessions. No-tick status is not automatically proof of market closure.

The download is restartable via its daily manifest and atomic file replacement. It stops if free disk falls below 10 GiB. Source files were preserved, and no account orders or strategy optimization occurred.

Next: investigate the 60 hourly discrepancies and empty weekday, verify account commission/swap assumptions, and implement independently checked Bid/Ask execution replay. No bot candidate is accepted yet. Existing negative preliminary screens and closed CRT/synthetic results remain unchanged.
