import pandas as pd
import pytest

from factor_registry.adapters import validate_bars


def test_validate_bars_sorts_and_normalises_timestamp() -> None:
    frame = pd.DataFrame(
        {
            "timestamp": ["2024-01-02", "2024-01-01"],
            "instrument": ["B", "A"],
            "close": [2.0, 1.0],
        }
    )
    result = validate_bars(frame, required_fields=("close",))
    assert result.timestamp.dt.tz is not None
    assert result.instrument.tolist() == ["A", "B"]


def test_validate_bars_rejects_duplicate_observations() -> None:
    frame = pd.DataFrame(
        {"timestamp": ["2024-01-01", "2024-01-01"], "instrument": ["A", "A"], "close": [1, 2]}
    )
    with pytest.raises(ValueError, match="unique"):
        validate_bars(frame)
