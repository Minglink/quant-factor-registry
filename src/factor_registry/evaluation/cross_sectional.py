"""Minimal, explicit cross-sectional factor diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable

import pandas as pd

from factor_registry.adapters.canonical import validate_bars
from factor_registry.core import FactorOutput


@dataclass(frozen=True)
class EvaluationReport:
    """Portable summary and timestamp-level diagnostics for a factor run."""

    summary: pd.DataFrame
    daily: pd.DataFrame
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


def evaluate_cross_sectional(
    factor: FactorOutput,
    bars: pd.DataFrame,
    horizons: Iterable[int] = (1, 5, 20),
    quantiles: int = 5,
) -> EvaluationReport:
    """Evaluate Rank IC and top-minus-bottom group returns at each horizon.

    This evaluator intentionally reports raw diagnostics only. Industry, market-cap and
    risk neutralisation must be explicitly enabled by a future risk-model extension.
    """

    if quantiles < 2:
        raise ValueError("quantiles must be at least 2")
    observations = factor.values.rename("factor").reset_index()
    daily_rows: list[pd.DataFrame] = []
    summary_rows: list[dict[str, float | int]] = []
    for horizon in horizons:
        if horizon < 1:
            raise ValueError("horizons must be positive")
        merged = observations.merge(_forward_returns(bars, horizon), on=["timestamp", "instrument"], how="inner")
        merged = merged.dropna(subset=["factor", "forward_return"])
        grouped = merged.groupby("timestamp", observed=True)
        daily = grouped.apply(
            lambda x: pd.Series(
                {
                    "rank_ic": x["factor"].rank().corr(x["forward_return"].rank()),
                    "quantile_spread": _quantile_spread(x, quantiles),
                    "coverage": len(x),
                }
            ),
        ).reset_index()
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
                "mean_quantile_spread": daily["quantile_spread"].mean(),
                "mean_coverage": daily["coverage"].mean(),
                "observations": len(merged),
            }
        )
    return EvaluationReport(
        summary=pd.DataFrame(summary_rows).set_index("horizon"),
        daily=pd.concat(daily_rows, ignore_index=True),
        assumptions={
            "quantiles": quantiles,
            "returns": "close-to-close, unadjusted for transaction costs",
            "neutralisation": "none",
        },
    )
