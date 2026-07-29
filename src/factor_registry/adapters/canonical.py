"""Validation for the project's canonical long-form market-data schema."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

IDENTIFIER_COLUMNS = ("timestamp", "instrument")


def validate_bars(frame: pd.DataFrame, required_fields: Iterable[str] = ()) -> pd.DataFrame:
    """Return a sorted copy after validating identifiers, fields and duplicate observations.

    Canonical bars are long-form observations. The timestamp identifies when data became
    known to the strategy; adapters are responsible for applying source-specific lags.
    """

    required = set(IDENTIFIER_COLUMNS).union(required_fields)
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")

    bars = frame.copy()
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
    if bars[list(IDENTIFIER_COLUMNS)].isna().any().any():
        raise ValueError("timestamp and instrument cannot contain missing values")
    if bars.duplicated(list(IDENTIFIER_COLUMNS)).any():
        raise ValueError("each (timestamp, instrument) observation must be unique")

    return bars.sort_values(list(IDENTIFIER_COLUMNS)).reset_index(drop=True)
