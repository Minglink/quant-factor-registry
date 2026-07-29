from factor_registry import evaluate_cross_sectional, reversal_5


def test_cross_sectional_report_has_requested_horizons(bars) -> None:
    report = evaluate_cross_sectional(reversal_5(bars), bars, horizons=(1, 5), quantiles=2)
    assert report.summary.index.tolist() == [1, 5]
    assert {"mean_rank_ic", "mean_quantile_spread", "mean_coverage"}.issubset(report.summary.columns)
    assert set(report.daily.horizon) == {1, 5}
