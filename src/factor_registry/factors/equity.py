"""Baseline daily equity factors using canonical long-form OHLCV bars."""

from __future__ import annotations

import numpy as np
import pandas as pd

from factor_registry.adapters.canonical import validate_bars
from factor_registry.core import AssetClass, FactorOutput, FactorSpec, Frequency


def _close_wide(bars: pd.DataFrame) -> pd.DataFrame:
    validated = validate_bars(bars, required_fields=("close",))
    return validated.pivot(index="timestamp", columns="instrument", values="close").sort_index()


def _as_output(spec: FactorSpec, values: pd.DataFrame) -> FactorOutput:
    series = values.stack().rename(spec.factor_id)
    series.index = series.index.set_names(["timestamp", "instrument"])
    return FactorOutput(spec=spec, values=series.dropna())


def momentum_12_1(bars: pd.DataFrame, lookback: int = 252, skip: int = 21) -> FactorOutput:
    """Return 12-1 momentum: cumulative return over [t-lookback, t-skip]."""

    if lookback <= skip:
        raise ValueError("lookback must be greater than skip")
    close = _close_wide(bars)
    values = close.shift(skip) / close.shift(lookback) - 1.0
    spec = FactorSpec(
        factor_id="momentum_12_1",
        name="12-1 Momentum",
        asset_classes=(AssetClass.CN_EQUITY, AssetClass.US_EQUITY),
        frequency=Frequency.DAILY,
        required_fields=("close",),
        lookback_periods=lookback,
        status="replicated",
        tags=("momentum", "price"),
    )
    return _as_output(spec, values)


def reversal_5(bars: pd.DataFrame, window: int = 5) -> FactorOutput:
    """Return the negative trailing return, a simple short-term reversal signal."""

    if window < 1:
        raise ValueError("window must be positive")
    close = _close_wide(bars)
    values = -(close / close.shift(window) - 1.0)
    spec = FactorSpec(
        factor_id="reversal_5",
        name="5-Day Reversal",
        asset_classes=(AssetClass.CN_EQUITY, AssetClass.US_EQUITY),
        frequency=Frequency.DAILY,
        required_fields=("close",),
        lookback_periods=window,
        status="replicated",
        tags=("reversal", "price"),
    )
    return _as_output(spec, values)


def volatility_20(bars: pd.DataFrame, window: int = 20) -> FactorOutput:
    """Return trailing standard deviation of log returns."""

    if window < 2:
        raise ValueError("window must be at least 2")
    close = _close_wide(bars)
    values = np.log(close).diff().rolling(window).std()
    spec = FactorSpec(
        factor_id="volatility_20",
        name="20-Day Realized Volatility",
        asset_classes=(AssetClass.CN_EQUITY, AssetClass.US_EQUITY),
        frequency=Frequency.DAILY,
        required_fields=("close",),
        lookback_periods=window,
        status="replicated",
        tags=("volatility", "risk"),
    )
    return _as_output(spec, values)


def amihud_illiquidity(bars: pd.DataFrame, window: int = 20) -> FactorOutput:
    """Return the rolling Amihud illiquidity proxy: |return| / traded value."""

    if window < 1:
        raise ValueError("window must be positive")
    validated = validate_bars(bars, required_fields=("close", "volume"))
    if "turnover" in validated.columns:
        traded_value = validated["turnover"]
    else:
        traded_value = validated["close"] * validated["volume"]
    daily = validated.assign(_illiq=validated.groupby("instrument")["close"].pct_change().abs() / traded_value)
    values = daily.pivot(index="timestamp", columns="instrument", values="_illiq").rolling(window).mean()
    spec = FactorSpec(
        factor_id="amihud_illiquidity_20",
        name="20-Day Amihud Illiquidity",
        asset_classes=(AssetClass.CN_EQUITY, AssetClass.US_EQUITY),
        frequency=Frequency.DAILY,
        required_fields=("close", "volume"),
        lookback_periods=window,
        status="replicated",
        tags=("liquidity", "microstructure"),
    )
    return _as_output(spec, values)
