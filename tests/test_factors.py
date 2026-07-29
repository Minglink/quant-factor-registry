from factor_registry import amihud_illiquidity, momentum_12_1, reversal_5, volatility_20


def test_daily_factor_outputs_have_canonical_index(bars) -> None:
    for factor in (momentum_12_1(bars), reversal_5(bars), volatility_20(bars), amihud_illiquidity(bars)):
        assert factor.values.index.names == ["timestamp", "instrument"]
        assert factor.values.name == factor.spec.factor_id
        assert not factor.values.empty


def test_momentum_skips_recent_window(bars) -> None:
    factor = momentum_12_1(bars, lookback=30, skip=5)
    assert factor.spec.lookback_periods == 30
    assert factor.values.index.get_level_values("timestamp").min() >= bars.timestamp.iloc[30]
