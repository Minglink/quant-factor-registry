"""Optional bridge for Qlib-style feature frames.

The adapter intentionally accepts a prepared DataFrame so users control their local
Qlib data and point-in-time universe instead of this package downloading market data.
"""

from __future__ import annotations

import pandas as pd

from factor_registry.adapters.canonical import validate_bars


def from_qlib(frame: pd.DataFrame, column_map: dict[str, str] | None = None) -> pd.DataFrame:
    """Convert a Qlib-like frame to canonical bars.

    `column_map` maps source columns to canonical names, for example
    `{"datetime": "timestamp", "instrument": "instrument", "$close": "close"}`.
    """

    mapping = column_map or {"datetime": "timestamp", "instrument": "instrument"}
    bars = frame.rename(columns=mapping)
    return validate_bars(bars)
