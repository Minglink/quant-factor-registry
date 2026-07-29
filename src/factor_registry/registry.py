"""Read the versioned, machine-readable factor registry."""

from __future__ import annotations

from pathlib import Path

import yaml


def load_registry(path: str | Path = "registry/factors") -> list[dict[str, object]]:
    """Load factor metadata files ordered by stable factor ID."""

    directory = Path(path)
    if not directory.is_dir():
        raise FileNotFoundError(f"factor registry directory not found: {directory}")
    factors: list[dict[str, object]] = []
    for file in sorted(directory.glob("*.yaml")):
        with file.open(encoding="utf-8") as handle:
            record = yaml.safe_load(handle)
        if not isinstance(record, dict) or "factor_id" not in record:
            raise ValueError(f"invalid factor registry record: {file}")
        factors.append(record)
    return sorted(factors, key=lambda item: str(item["factor_id"]))
