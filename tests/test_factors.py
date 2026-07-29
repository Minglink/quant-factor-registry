from factor_registry import (
    amihud_illiquidity,
    average_dollar_volume_20,
    downside_volatility_20,
    high_low_range_20,
    momentum_12_1,
    momentum_20,
    momentum_60,
    return_skewness_20,
    reversal_5,
    reversal_20,
    volatility_20,
    volume_price_correlation_20,
    volume_volatility_20,
)


def test_daily_factor_outputs_have_canonical_index(bars) -> None:
    for factor in (momentum_12_1(bars), reversal_5(bars), volatility_20(bars), amihud_illiquidity(bars)):
        assert factor.values.index.names == ["timestamp", "instrument"]
        assert factor.values.name == factor.spec.factor_id
        assert not factor.values.empty


def test_momentum_skips_recent_window(bars) -> None:
    factor = momentum_12_1(bars, lookback=30, skip=5)
    assert factor.spec.lookback_periods == 30
    assert factor.values.index.get_level_values("timestamp").min() >= bars.timestamp.iloc[30]


def test_ohlcv_factor_batch_has_canonical_output(bars) -> None:
    enriched = bars.assign(
        high=bars.close * 1.01,
        low=bars.close * 0.99,
        volume=bars.volume * (1.0 + (bars.index % 7) / 100.0),
    )
    factors = (
        momentum_20(enriched), momentum_60(enriched), reversal_20(enriched),
        downside_volatility_20(enriched), high_low_range_20(enriched),
        average_dollar_volume_20(enriched), volume_volatility_20(enriched),
        volume_price_correlation_20(enriched), return_skewness_20(enriched),
    )
    assert all(factor.spec.asset_classes[0].value == "cn_equity" for factor in factors)
    assert all(not factor.values.empty for factor in factors)
