"""Tests for coordinator helpers."""

from __future__ import annotations

import json
import os
import asyncio
from pathlib import Path
from typing import Any


from custom_components.ecotrend_ista.coordinator import IstaDataUpdateCoordinator, create_directory_file


class DummyConfig:
    """Provide a minimal config object with a path helper."""

    def __init__(self, base: str) -> None:
        self._base = base

    def path(self, *paths: str) -> str:
        return os.path.join(self._base, *paths)


class DummyHass:
    """Simplified hass object for coordinator tests."""

    def __init__(self, base: str) -> None:
        self.config = DummyConfig(base)

    async def async_add_executor_job(self, func, *args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)


class DummyRaw:
    """Minimal replacement for the CustomRaw object."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def to_dict(self) -> dict[str, Any]:
        return self._payload


def test_create_directory_file_writes_expected_json(tmp_path: Path) -> None:
    """The helper should create the target folder and write the JSON representation."""

    hass = DummyHass(str(tmp_path))
    payload = {"value": 42}
    consum_raw = DummyRaw(payload)

    asyncio.run(create_directory_file(hass, consum_raw, "support"))

    target_file = tmp_path / "www" / "ecotrend_ista_support.json"
    assert target_file.exists()

    with target_file.open(encoding="utf-8") as file:
        data = json.load(file)

    assert data == payload


class DummyEntry:
    """Simple config entry stand-in used by coordinator tests."""

    def __init__(self, options: dict[str, Any], data: dict[str, Any] | None = None) -> None:
        self.options = options
        self.data = data or {}


class DummyDkController:
    """DK controller stand-in exposing methods used by _fetch_dk_data."""

    def get_meter_types(self) -> dict[str, Any]:
        return {
            "electricity": {"unit": "kWh"},
            "heat": {"unit": "Delinger"},
        }

    def get_electricity_consumption_day(self) -> list[dict[str, Any]]:
        return [{"value": None}, {"value": 5}]

    def get_electricity_economy_day(self) -> list[dict[str, Any]]:
        return [{"priceValue": None}, {"priceValue": 12}]

    def get_heat_consumption_day(self) -> list[dict[str, Any]]:
        return [{"value": None}, {"value": 7}]

    def get_heat_economy_day(self) -> list[dict[str, Any]]:
        return [{"priceValue": None}, {"priceValue": 20}]

    def get_user_info(self) -> dict[str, Any]:
        return {"Name": "DK User", "Language": "da-DK"}


class DummyDeController:
    """DE controller stand-in exposing get_uuids for delegation checks."""

    def get_uuids(self) -> list[str]:
        return ["de-uuid-1", "de-uuid-2"]


def test_dk_fetch_data_maps_values_for_sensors() -> None:
    """DK payload should expose the latest numeric values and units used by DK sensors."""

    coordinator = object.__new__(IstaDataUpdateCoordinator)
    coordinator.controller = DummyDkController()

    payload = coordinator._fetch_dk_data()

    assert payload["dk"]["electricity_consumption"] == 5.0
    assert payload["dk"]["electricity_economy"] == 12.0
    assert payload["dk"]["heat_consumption"] == 7.0
    assert payload["dk"]["heat_economy"] == 20.0
    assert payload["dk"]["electricity_unit"] == "kWh"
    assert payload["dk"]["heat_unit"] == "Delinger"
    assert payload["dk"]["currency_unit"] == "kr"
    assert payload["dk"]["user_info"]["Name"] == "DK User"


def test_get_uuids_returns_dk_synthetic_uuid() -> None:
    """DK mode should provide one synthetic UUID for entity creation."""

    coordinator = object.__new__(IstaDataUpdateCoordinator)
    coordinator._entry = DummyEntry(options={"URL": "dk_url"}, data={})
    coordinator.controller = DummyDkController()

    assert coordinator.get_uuids() == ["dk"]


def test_get_uuids_delegates_for_de_mode() -> None:
    """DE mode should delegate UUID retrieval to the DE controller."""

    coordinator = object.__new__(IstaDataUpdateCoordinator)
    coordinator._entry = DummyEntry(options={"URL": "de_url"}, data={})
    coordinator.controller = DummyDeController()

    assert coordinator.get_uuids() == ["de-uuid-1", "de-uuid-2"]


def test_async_update_data_uses_dk_branch() -> None:
    """DK mode update should call _fetch_dk_data and set coordinator data."""

    coordinator = object.__new__(IstaDataUpdateCoordinator)
    coordinator._entry = DummyEntry(options={"URL": "dk_url"}, data={})
    coordinator.hass = DummyHass(base=".")
    coordinator.data = None

    async def _init() -> None:
        return None

    expected_data = {"dk": {"electricity_consumption": 3.0}}
    coordinator.init = _init
    coordinator._fetch_dk_data = lambda: expected_data
    coordinator.async_set_updated_data = lambda data: setattr(coordinator, "_updated_data", data)

    result = asyncio.run(coordinator._async_update_data())

    assert result == expected_data
    assert coordinator.data == expected_data
    assert coordinator._updated_data == expected_data
