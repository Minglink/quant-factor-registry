"""Minimal, explicit cross-sectional factor diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable
from typing import Callable

import pandas as pd

from factor_registry.adapters.canonical import validate_bars
from factor_registry.core import FactorOutput


@dataclass(frozen=True)
class EvaluationReport:
    """Portable summary and timestamp-level diagnostics for a factor run."""

    summary: pd.DataFrame
    daily: pd.DataFrame
    stability: pd.DataFrame
    assumptions: dict[str, object]


def _forward_returns(bars: pd.DataFrame, horizon: int) -> pd.DataFrame:
    close = validate_bars(bars, required_fields=("close",)).pivot(
        index="timestamp", columns="instrument", values="close"
    )
    result = close.shift(-horizon) / close - 1.0
    return result.stack().rename("forward_return").rename_axis(["timestamp", "instrument"]).reset_index()


def _quantile_spread(frame: pd.DataFrame, quantiles: int) -> float:
    if len(frame) < quantiles:
        return float("nan")
    ranked = frame["factor"].rank(method="first")
    bucket = pd.qcut(ranked, q=quantiles, labels=False, duplicates="drop")
    grouped = frame.assign(bucket=bucket).groupby("bucket", observed=True)["forward_return"].mean()
    return float(grouped.iloc[-1] - grouped.iloc[0]) if len(grouped) >= 2 else float("nan")


def _quantile_labels(values: pd.Series, quantiles: int) -> pd.Series:
    if len(values) < quantiles:
        return pd.Series(float("nan"), index=values.index)
    ranked = values.rank(method="first")
    return pd.qcut(ranked, q=quantiles, labels=False, duplicates="drop").astype("float64")


def _portfolio_turnover(assignments: pd.DataFrame, quantiles: int) -> pd.Series:
    """Estimate one-way turnover from changing top and bottom quantile memberships."""

    rows: list[dict[str, object]] = []
    previous_long: set[str] | None = None
    previous_short: set[str] | None = None
    top = float(quantiles - 1)
    for timestamp, frame in assignments.groupby("timestamp", observed=True):
        long_members = set(frame.loc[frame["quantile"] == top, "instrument"])
        short_members = set(frame.loc[frame["quantile"] == 0.0, "instrument"])
        if previous_long is None or previous_short is None:
            turnover = float("nan")
        else:
            long_turnover = 1.0 - len(long_members.intersection(previous_long)) / max(len(previous_long), 1)
            short_turnover = 1.0 - len(short_members.intersection(previous_short)) / max(len(previous_short), 1)
            turnover = (long_turnover + short_turnover) / 2.0
        rows.append({"timestamp": timestamp, "quantile_turnover": turnover})
        previous_long = long_members
        previous_short = short_members
    return pd.DataFrame(rows).set_index("timestamp")["quantile_turnover"]


def evaluate_cross_sectional(
    factor: FactorOutput,
    bars: pd.DataFrame,
    horizons: Iterable[int] = (1, 5, 20),
    quantiles: int = 5,
    one_way_cost_bps: float = 0.0,
    regimes: pd.Series | None = None,
    preprocess: Callable[[pd.DataFrame], pd.DataFrame] | None = None,
) -> EvaluationReport:
    """Evaluate Rank IC and top-minus-bottom group returns at each horizon.

    ``preprocess`` is an explicit integration hook for point-in-time industry, size or
    risk-model neutralisation. It receives the timestamped observation frame and must
    return a frame containing the same identifiers plus ``factor`` and ``forward_return``.
    """

    if quantiles < 2:
        raise ValueError("quantiles must be at least 2")
    if one_way_cost_bps < 0:
        raise ValueError("one_way_cost_bps cannot be negative")
    if regimes is not None:
        if not isinstance(regimes.index, pd.DatetimeIndex):
            raise ValueError("regimes must use a DatetimeIndex of timestamps")
        regimes = regimes.copy()
        regimes.index = pd.to_datetime(regimes.index, utc=True)
        regimes.name = regimes.name or "regime"
    observations = factor.values.rename("factor").reset_index()
    daily_rows: list[pd.DataFrame] = []
    summary_rows: list[dict[str, float | int]] = []
    stability_rows: list[pd.DataFrame] = []
    for horizon in horizons:
        if horizon < 1:
            raise ValueError("horizons must be positive")
        merged = observations.merge(_forward_returns(bars, horizon), on=["timestamp", "instrument"], how="inner")
        merged = merged.dropna(subset=["factor", "forward_return"])
        if preprocess is not None:
            merged = preprocess(merged.copy())
            required = {"timestamp", "instrument", "factor", "forward_return"}
            if not required.issubset(merged.columns):
                raise ValueError("preprocess must retain timestamp, instrument, factor and forward_return")
        assignments = merged.copy()
        assignments["quantile"] = assignments.groupby("timestamp", observed=True)["factor"].transform(
            _quantile_labels, quantiles=quantiles
        )
        grouped = assignments.groupby("timestamp", observed=True)
        daily = grouped.apply(
            lambda x: pd.Series(
                {
                    "rank_ic": x["factor"].rank().corr(x["forward_return"].rank()),
                    "gross_quantile_spread": _quantile_spread(x, quantiles),
                    "coverage": len(x),
                }
            ),
        ).reset_index()
        daily = daily.join(_portfolio_turnover(assignments, quantiles), on="timestamp")
        daily["estimated_cost"] = daily["quantile_turnover"] * one_way_cost_bps / 10_000.0
        daily["net_quantile_spread"] = daily["gross_quantile_spread"] - daily["estimated_cost"]
        daily["long_short_nav"] = (1.0 + daily["net_quantile_spread"].fillna(0.0)).cumprod()
        daily["quantile_spread"] = daily["gross_quantile_spread"]
        daily["horizon"] = horizon
        daily_rows.append(daily)
        rank_ic_std = daily["rank_ic"].std()
        rank_ic_ir = (
            daily["rank_ic"].mean() / rank_ic_std
            if pd.notna(rank_ic_std) and rank_ic_std > 0
            else float("nan")
        )
        summary_rows.append(
            {
                "horizon": horizon,
                "mean_rank_ic": daily["rank_ic"].mean(),
                "rank_ic_ir": rank_ic_ir,
                "mean_quantile_spread": daily["gross_quantile_spread"].mean(),
                "mean_net_quantile_spread": daily["net_quantile_spread"].mean(),
                "mean_quantile_turnover": daily["quantile_turnover"].mean(),
                "mean_coverage": daily["coverage"].mean(),
                "observations": len(merged),
            }
        )
        if regimes is not None:
            by_regime = daily.join(regimes, on="timestamp").dropna(subset=[regimes.name])
            if not by_regime.empty:
                stability = (
                    by_regime.groupby(regimes.name, observed=True)
                    .agg(
                        mean_rank_ic=("rank_ic", "mean"),
                        mean_net_quantile_spread=("net_quantile_spread", "mean"),
                        mean_quantile_turnover=("quantile_turnover", "mean"),
                        periods=("timestamp", "size"),
                    )
                    .reset_index()
                )
                stability["horizon"] = horizon
                stability_rows.append(stability)
    return EvaluationReport(
        summary=pd.DataFrame(summary_rows).set_index("horizon"),
        daily=pd.concat(daily_rows, ignore_index=True),
        stability=pd.concat(stability_rows, ignore_index=True)
        if stability_rows
        else pd.DataFrame(
            columns=["horizon", "regime", "mean_rank_ic", "mean_net_quantile_spread", "mean_quantile_turnover", "periods"]
        ),
        assumptions={
            "quantiles": quantiles,
            "returns": "close-to-close forward returns",
            "one_way_cost_bps": one_way_cost_bps,
            "neutralisation": "custom preprocess" if preprocess is not None else "none",
            "regimes": regimes.name if regimes is not None else "none",
        },
    )
