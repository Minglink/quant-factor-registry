"""Structural checks that make registry entries independently auditable."""

from __future__ import annotations

import importlib
import re
from pathlib import Path

from factor_registry.core import AssetClass, Frequency
from factor_registry.registry import load_registry


VALID_STATUSES = {"experimental", "replicated", "validated", "deprecated"}
VALID_CATEGORIES = {
    "momentum", "reversal", "volatility", "liquidity", "valuation", "quality", "growth", "size",
}
REQUIRED_FIELDS = {
    "factor_id", "name", "name_zh", "category", "status", "asset_classes", "frequency", "required_fields",
    "lookback_periods", "availability_lag", "availability_policy", "source_urls", "source_license",
    "version", "implementation", "card",
}
FACTOR_ID = re.compile(r"^[a-z][a-z0-9_]*$")


class RegistryValidationError(ValueError):
    """Raised when a registry entry cannot support a reproducible factor run."""


def _implementation_exists(reference: str) -> bool:
    module_name, separator, attribute = reference.partition(":")
    if not separator or not module_name or not attribute:
        return False
    try:
        return callable(getattr(importlib.import_module(module_name), attribute))
    except (AttributeError, ImportError):
        return False


def validate_registry(path: str | Path = "registry/factors") -> list[dict[str, object]]:
    """Load and validate every registry record, cards, provenance and implementation.

    This deliberately verifies structure only. Numerical replication is covered by factor
    tests and reproducible experiment configurations, not by metadata validation.
    """

    directory = Path(path)
    root = directory.resolve().parents[1]
    records = load_registry(directory)
    seen_ids: set[str] = set()
    for record in records:
        factor_id = str(record.get("factor_id", ""))
        missing = sorted(REQUIRED_FIELDS.difference(record))
        if missing:
            raise RegistryValidationError(f"{factor_id or 'unknown'}: missing fields: {', '.join(missing)}")
        if not FACTOR_ID.fullmatch(factor_id) or factor_id in seen_ids:
            raise RegistryValidationError(f"invalid or duplicate factor_id: {factor_id}")
        seen_ids.add(factor_id)
        if record["status"] not in VALID_STATUSES:
            raise RegistryValidationError(f"{factor_id}: invalid status")
        if record["category"] not in VALID_CATEGORIES:
            raise RegistryValidationError(f"{factor_id}: invalid category")
        if record["frequency"] not in {item.value for item in Frequency}:
            raise RegistryValidationError(f"{factor_id}: invalid frequency")
        if not set(record["asset_classes"]).issubset({item.value for item in AssetClass}):
            raise RegistryValidationError(f"{factor_id}: invalid asset class")
        if not {"timestamp", "instrument"}.issubset(record["required_fields"]):
            raise RegistryValidationError(f"{factor_id}: identifier fields must be declared")
        if not record["source_urls"] or not all(str(url).startswith(("https://", "http://")) for url in record["source_urls"]):
            raise RegistryValidationError(f"{factor_id}: source_urls must contain absolute URLs")
        if not str(record["source_license"]).strip() or not str(record["availability_policy"]).strip():
            raise RegistryValidationError(f"{factor_id}: provenance and availability policy are required")
        if not (root / str(record["card"])).is_file():
            raise RegistryValidationError(f"{factor_id}: factor card does not exist")
        if not _implementation_exists(str(record["implementation"])):
            raise RegistryValidationError(f"{factor_id}: implementation does not resolve to a callable")
    return records
