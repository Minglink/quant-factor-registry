"""The portable factor contract shared by all asset-class extensions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

import pandas as pd


class AssetClass(str, Enum):
    CN_EQUITY = "cn_equity"
    US_EQUITY = "us_equity"
    FUTURES = "futures"
    CRYPTO = "crypto"
    HIGH_FREQUENCY = "high_frequency"


class Frequency(str, Enum):
    DAILY = "1d"
    HOURLY = "1h"
    MINUTE = "1m"
    TICK = "tick"


@dataclass(frozen=True)
class FactorSpec:
    """Metadata needed to execute and audit a factor without hidden assumptions."""

    factor_id: str
    name: str
    asset_classes: tuple[AssetClass, ...]
    frequency: Frequency
    required_fields: tuple[str, ...]
    availability_lag: pd.Timedelta = pd.Timedelta(0)
    lookback_periods: int = 0
    universe_rule: str = "liquid_instruments_only"
    status: str = "experimental"
    source_urls: tuple[str, ...] = ()
    execution_notes: str = ""
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class FactorOutput:
    """A timestamped cross-sectional factor series with immutable provenance."""

    spec: FactorSpec
    values: pd.Series
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.values.index, pd.MultiIndex) or self.values.index.nlevels != 2:
            raise ValueError("factor values must use a (timestamp, instrument) MultiIndex")
        if list(self.values.index.names) != ["timestamp", "instrument"]:
            raise ValueError("factor index names must be ['timestamp', 'instrument']")
        if self.values.name != self.spec.factor_id:
            raise ValueError("factor series name must equal FactorSpec.factor_id")
