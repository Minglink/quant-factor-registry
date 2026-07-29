import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def bars() -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", periods=300, freq="B", tz="UTC")
    rows = []
    for idx, instrument in enumerate(["000001.SZ", "000002.SZ", "000003.SZ", "000004.SZ"]):
        prices = 10 + idx + np.linspace(0, 3 + idx, len(dates))
        for date, close in zip(dates, prices, strict=True):
            rows.append(
                {
                    "timestamp": date,
                    "instrument": instrument,
                    "close": close,
                    "volume": 1_000_000 + idx * 10_000,
                }
            )
    return pd.DataFrame(rows)
