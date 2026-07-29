from pathlib import Path

from factor_registry.registry import load_registry


def test_registry_records_have_factor_cards() -> None:
    root = Path(__file__).parents[1]
    records = load_registry(root / "registry" / "factors")
    assert len(records) >= 4
    for record in records:
        assert (root / str(record["card"])).is_file()
