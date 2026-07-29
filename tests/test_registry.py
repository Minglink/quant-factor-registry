from pathlib import Path

from factor_registry.registry import load_registry
from factor_registry.registry_validation import validate_registry


def test_registry_records_have_factor_cards() -> None:
    root = Path(__file__).parents[1]
    records = load_registry(root / "registry" / "factors")
    assert len(records) >= 4
    for record in records:
        assert (root / str(record["card"])).is_file()


def test_registry_records_resolve_to_implemented_factor_functions() -> None:
    root = Path(__file__).parents[1]
    records = validate_registry(root / "registry" / "factors")
    assert {record["factor_id"] for record in records} == {
        "amihud_illiquidity_20",
        "average_dollar_volume_20",
        "downside_volatility_20",
        "high_low_range_20",
        "momentum_12_1",
        "momentum_20",
        "momentum_60",
        "return_skewness_20",
        "reversal_5",
        "reversal_20",
        "volatility_20",
        "volume_price_correlation_20",
        "volume_volatility_20",
    }
