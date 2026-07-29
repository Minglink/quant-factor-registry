from factor_registry import evaluate_cross_sectional, reversal_5


def test_cross_sectional_report_has_requested_horizons(bars) -> None:
    report = evaluate_cross_sectional(reversal_5(bars), bars, horizons=(1, 5), quantiles=2)
    assert report.summary.index.tolist() == [1, 5]
    assert {"mean_rank_ic", "mean_quantile_spread", "mean_coverage"}.issubset(report.summary.columns)
    assert set(report.daily.horizon) == {1, 5}


def test_cross_sectional_report_tracks_cost_turnover_and_regimes(bars) -> None:
    regimes = bars.drop_duplicates("timestamp").set_index("timestamp")["close"].map(lambda value: "up" if value > 12 else "down")
    report = evaluate_cross_sectional(
        reversal_5(bars), bars, horizons=(1,), quantiles=2, one_way_cost_bps=10, regimes=regimes
    )
    assert {"quantile_turnover", "estimated_cost", "net_quantile_spread", "long_short_nav"}.issubset(report.daily.columns)
    assert report.assumptions["one_way_cost_bps"] == 10
    assert {"mean_rank_ic", "mean_net_quantile_spread", "periods"}.issubset(report.stability.columns)
