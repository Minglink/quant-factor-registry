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


def _rolling_return(bars: pd.DataFrame, window: int, factor_id: str, name: str) -> FactorOutput:
    if window < 1:
        raise ValueError("window must be positive")
    close = _close_wide(bars)
    values = close / close.shift(window) - 1.0
    spec = FactorSpec(
        factor_id=factor_id,
        name=name,
        category="momentum",
        asset_classes=(AssetClass.CN_EQUITY,),
        frequency=Frequency.DAILY,
        required_fields=("close",),
        lookback_periods=window,
        status="replicated",
        tags=("momentum", "price"),
    )
    return _as_output(spec, values)


def momentum_12_1(bars: pd.DataFrame, lookback: int = 252, skip: int = 21) -> FactorOutput:
    """Return 12-1 momentum: cumulative return over [t-lookback, t-skip]."""

    if lookback <= skip:
        raise ValueError("lookback must be greater than skip")
    close = _close_wide(bars)
    values = close.shift(skip) / close.shift(lookback) - 1.0
    spec = FactorSpec(
        factor_id="momentum_12_1",
        name="12-1 Momentum",
        category="momentum",
        asset_classes=(AssetClass.CN_EQUITY,),
        frequency=Frequency.DAILY,
        required_fields=("close",),
        lookback_periods=lookback,
        status="replicated",
        tags=("momentum", "price"),
    )
    return _as_output(spec, values)


def momentum_20(bars: pd.DataFrame, window: int = 20) -> FactorOutput:
    """Return the trailing 20-trading-day cumulative return."""

    return _rolling_return(bars, window, "momentum_20", "20-Day Momentum")


def momentum_60(bars: pd.DataFrame, window: int = 60) -> FactorOutput:
    """Return the trailing 60-trading-day cumulative return."""

    return _rolling_return(bars, window, "momentum_60", "60-Day Momentum")


def reversal_5(bars: pd.DataFrame, window: int = 5) -> FactorOutput:
    """Return the negative trailing return, a simple short-term reversal signal."""

    if window < 1:
        raise ValueError("window must be positive")
    close = _close_wide(bars)
    values = -(close / close.shift(window) - 1.0)
    spec = FactorSpec(
        factor_id="reversal_5",
        name="5-Day Reversal",
        category="reversal",
        asset_classes=(AssetClass.CN_EQUITY,),
        frequency=Frequency.DAILY,
        required_fields=("close",),
        lookback_periods=window,
        status="replicated",
        tags=("reversal", "price"),
    )
    return _as_output(spec, values)


def reversal_20(bars: pd.DataFrame, window: int = 20) -> FactorOutput:
    """Return the negative trailing 20-trading-day return."""

    if window < 1:
        raise ValueError("window must be positive")
    close = _close_wide(bars)
    values = -(close / close.shift(window) - 1.0)
    spec = FactorSpec(
        factor_id="reversal_20",
        name="20-Day Reversal",
        category="reversal",
        asset_classes=(AssetClass.CN_EQUITY,),
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
        category="volatility",
        asset_classes=(AssetClass.CN_EQUITY,),
        frequency=Frequency.DAILY,
        required_fields=("close",),
        lookback_periods=window,
        status="replicated",
        tags=("volatility", "risk"),
    )
    return _as_output(spec, values)


def downside_volatility_20(bars: pd.DataFrame, window: int = 20) -> FactorOutput:
    """Return the trailing deviation of negative daily returns only."""

    if window < 2:
        raise ValueError("window must be at least 2")
    returns = _close_wide(bars).pct_change().clip(upper=0.0)
    values = returns.rolling(window).std()
    spec = FactorSpec(
        factor_id="downside_volatility_20",
        name="20-Day Downside Volatility",
        category="volatility",
        asset_classes=(AssetClass.CN_EQUITY,),
        frequency=Frequency.DAILY,
        required_fields=("close",),
        lookback_periods=window,
        status="replicated",
        tags=("volatility", "downside_risk"),
    )
    return _as_output(spec, values)


def high_low_range_20(bars: pd.DataFrame, window: int = 20) -> FactorOutput:
    """Return the rolling mean intraday high-low range scaled by close."""

    if window < 1:
        raise ValueError("window must be positive")
    validated = validate_bars(bars, required_fields=("high", "low", "close"))
    daily_range = (validated["high"] - validated["low"]) / validated["close"]
    values = (
        validated.assign(_range=daily_range)
        .pivot(index="timestamp", columns="instrument", values="_range")
        .rolling(window)
        .mean()
    )
    spec = FactorSpec(
        factor_id="high_low_range_20",
        name="20-Day High-Low Range",
        category="volatility",
        asset_classes=(AssetClass.CN_EQUITY,),
        frequency=Frequency.DAILY,
        required_fields=("high", "low", "close"),
        lookback_periods=window,
        status="replicated",
        tags=("volatility", "range"),
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
        category="liquidity",
        asset_classes=(AssetClass.CN_EQUITY,),
        frequency=Frequency.DAILY,
        required_fields=("close", "volume"),
        lookback_periods=window,
        status="replicated",
        tags=("liquidity", "microstructure"),
    )
    return _as_output(spec, values)


def average_dollar_volume_20(bars: pd.DataFrame, window: int = 20) -> FactorOutput:
    """Return average daily traded value, using turnover when supplied."""

    if window < 1:
        raise ValueError("window must be positive")
    validated = validate_bars(bars, required_fields=("close", "volume"))
    traded_value = validated["turnover"] if "turnover" in validated else validated["close"] * validated["volume"]
    values = (
        validated.assign(_dollar_volume=traded_value)
        .pivot(index="timestamp", columns="instrument", values="_dollar_volume")
        .rolling(window)
        .mean()
    )
    spec = FactorSpec(
        factor_id="average_dollar_volume_20",
        name="20-Day Average Dollar Volume",
        category="liquidity",
        asset_classes=(AssetClass.CN_EQUITY,),
        frequency=Frequency.DAILY,
        required_fields=("close", "volume"),
        lookback_periods=window,
        status="replicated",
        tags=("liquidity", "volume"),
    )
    return _as_output(spec, values)


def volume_volatility_20(bars: pd.DataFrame, window: int = 20) -> FactorOutput:
    """Return the trailing standard deviation of log traded volume."""

    if window < 2:
        raise ValueError("window must be at least 2")
    validated = validate_bars(bars, required_fields=("volume",))
    if (validated["volume"] <= 0).any():
        raise ValueError("volume must be positive for log-volume volatility")
    values = (
        validated.assign(_log_volume=np.log(validated["volume"]))
        .pivot(index="timestamp", columns="instrument", values="_log_volume")
        .rolling(window)
        .std()
    )
    spec = FactorSpec(
        factor_id="volume_volatility_20",
        name="20-Day Volume Volatility",
        category="liquidity",
        asset_classes=(AssetClass.CN_EQUITY,),
        frequency=Frequency.DAILY,
        required_fields=("volume",),
        lookback_periods=window,
        status="replicated",
        tags=("liquidity", "volume"),
    )
    return _as_output(spec, values)


def volume_price_correlation_20(bars: pd.DataFrame, window: int = 20) -> FactorOutput:
    """Return rolling correlation between daily return and log-volume change."""

    if window < 2:
        raise ValueError("window must be at least 2")
    validated = validate_bars(bars, required_fields=("close", "volume"))
    if (validated["volume"] <= 0).any():
        raise ValueError("volume must be positive for log-volume changes")
    close = validated.pivot(index="timestamp", columns="instrument", values="close").sort_index()
    volume = validated.pivot(index="timestamp", columns="instrument", values="volume").sort_index()
    values = close.pct_change().rolling(window).corr(np.log(volume).diff())
    spec = FactorSpec(
        factor_id="volume_price_correlation_20",
        name="20-Day Volume-Price Correlation",
        category="liquidity",
        asset_classes=(AssetClass.CN_EQUITY,),
        frequency=Frequency.DAILY,
        required_fields=("close", "volume"),
        lookback_periods=window,
        status="replicated",
        tags=("liquidity", "volume", "price"),
    )
    return _as_output(spec, values)


def return_skewness_20(bars: pd.DataFrame, window: int = 20) -> FactorOutput:
    """Return trailing sample skewness of simple daily returns."""

    if window < 3:
        raise ValueError("window must be at least 3")
    values = _close_wide(bars).pct_change().rolling(window).skew()
    spec = FactorSpec(
        factor_id="return_skewness_20",
        name="20-Day Return Skewness",
        category="volatility",
        asset_classes=(AssetClass.CN_EQUITY,),
        frequency=Frequency.DAILY,
        required_fields=("close",),
        lookback_periods=window,
        status="replicated",
        tags=("volatility", "distribution"),
    )
    return _as_output(spec, values)
