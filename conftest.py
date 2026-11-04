"""Test-session setup for the EURUSD research scripts.

Several research modules under EURUSD_research/ read a small, non-sensitive
TRAIN/VALIDATION/OOS split-boundary file at *import time*:

    CRT_research/data/Claude_split_boundaries_EURUSD.json

That file (and the raw_data/ and CRT_research/ folders generally) is
intentionally gitignored because the folders also hold large local-only
market data. This means a fresh clone (and CI) has no boundary file at all,
so importing e.g. C_crt_sd_structural_01.py fails before any test runs.

The boundary values themselves are not secret -- they are plain calendar
dates and are already published in this repo's own research notes (see
EURUSD_research/C_EURUSD_CRT_SD_FROZEN_01.md). This fixture recreates that
file (only if it is not already present -- a real local copy is never
overwritten) so the pure-logic unit tests can import and run without any
live market data or MetaTrader5 connection.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
_BOUNDARIES_PATH = ROOT / "CRT_research" / "data" / "Claude_split_boundaries_EURUSD.json"

_FROZEN_BOUNDARIES = {
    "train_start": "2022-11-01T00:00:00",
    "train_end": "2025-05-06T15:00:00",
    "val_start": "2025-05-06T16:00:00",
    "val_end": "2026-01-08T20:00:00",
    "oos_start": "2026-01-08T21:00:00",
}


def pytest_configure(config):
    if _BOUNDARIES_PATH.exists():
        return
    _BOUNDARIES_PATH.parent.mkdir(parents=True, exist_ok=True)
    _BOUNDARIES_PATH.write_text(json.dumps(_FROZEN_BOUNDARIES, indent=2))
