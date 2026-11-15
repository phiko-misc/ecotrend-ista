"""Tests for coordinator helpers."""

from __future__ import annotations

import asyncio
from typing import Any

from custom_components.ecotrend_ista import coordinator as coordinator_module
from custom_components.ecotrend_ista.coordinator import IstaDataUpdateCoordinator
import pytest


class DummyHass:
    """Simplified hass object for coordinator tests."""

    def __init__(self, base: str = ".") -> None:
        del base

    async def async_add_executor_job(self, func, *args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)


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

    def get_electricity_consumption_billing(self) -> list[dict[str, Any]]:
        return [{"value": None}, {"value": 50}]

    def get_electricity_economy_day(self) -> list[dict[str, Any]]:
        return [{"priceValue": None}, {"priceValue": 12}]

    def get_heat_consumption_day(self) -> list[dict[str, Any]]:
        return [{"value": None}, {"value": 7}]

    def get_heat_consumption_billing(self) -> list[dict[str, Any]]:
        return [{"value": None}, {"value": 70}]

    def get_heat_economy_day(self) -> list[dict[str, Any]]:
        return [{"priceValue": None}, {"priceValue": 20}]

    def get_user_info(self) -> dict[str, Any]:
        return {"Name": "DK User", "Language": "da-DK"}

    def get_user_settings(self) -> dict[str, Any]:
        return {
            "Phone": "+4512345678",
            "receiveNotification": True,
            "receiveNotificationByPhone": True,
            "receiveNotificationByMail": False,
        }

    def get_meters(self) -> dict[str, Any]:
        return {
            "Meters": {
                "Value": [
                    {
                        "METER_ID": 123,
                        "METER_NO": "M-123",
                        "MeterText": "Electricity",
                        "MeterType": "EL",
                        "Unit": "kWh",
                        "Last_Meter_Reading": 42,
                    },
                    {
                        "METER_ID": 456,
                        "MeterText": "Røg",
                        "MeterType": "SMOKE",
                        "Message": "Battery low",
                        "Headline": None,
                    },
                ]
            }
        }


class DummyDkControllerPartialFailure(DummyDkController):
    """DK controller stand-in where one graph endpoint fails."""

    def get_electricity_consumption_day(self) -> list[dict[str, Any]]:
        raise RuntimeError("404 Not Found")


def test_dk_fetch_data_maps_values_for_sensors() -> None:
    """DK payload should expose the latest numeric values and units used by DK sensors."""

    coordinator = object.__new__(IstaDataUpdateCoordinator)
    coordinator.controller = DummyDkController()

    payload = coordinator._fetch_dk_data()

    assert payload["dk"]["electricity_consumption"] == 50.0
    assert payload["dk"]["electricity_costs_billing"] is None
    assert payload["dk"]["heating_consumption"] == 70.0
    assert payload["dk"]["heating_costs_billing"] is None
    assert payload["dk"]["electricity_unit"] == "kWh"
    assert payload["dk"]["heat_unit"] == "Delinger"
    assert payload["dk"]["currency_unit"] == "DKK"
    assert payload["dk"]["user_info"]["Name"] == "DK User"
    assert payload["dk"]["user_settings"]["receiveNotificationByPhone"] is True
    assert payload["dk"]["meters"][0]["METER_ID"] == 123
    assert payload["dk"]["meters"][1]["smoke_status"] == "battery_low"
    assert payload["dk"]["graph_history"]["electricity"]["consumption"]["billing"] == [{"value": None}, {"value": 50}]


def test_dk_fetch_data_handles_partial_endpoint_failures() -> None:
    """DK payload fetch should continue when a single endpoint fails (e.g. 404)."""

    coordinator = object.__new__(IstaDataUpdateCoordinator)
    coordinator.controller = DummyDkControllerPartialFailure()

    payload = coordinator._fetch_dk_data()

    assert payload["dk"]["electricity_consumption"] == 50.0
    assert payload["dk"]["electricity_costs_billing"] is None
    assert payload["dk"]["heating_consumption"] == 70.0
    assert payload["dk"]["heating_costs_billing"] is None


def test_get_uuids_returns_dk_synthetic_uuid() -> None:
    """DK mode should provide one synthetic UUID for entity creation."""

    coordinator = object.__new__(IstaDataUpdateCoordinator)
    coordinator._entry = DummyEntry(options={"URL": "dk_url"}, data={})
    coordinator.controller = DummyDkController()

    assert coordinator.get_uuids() == ["dk"]


def test_async_update_data_uses_dk_branch() -> None:
    """DK mode update should call _fetch_dk_data and set coordinator data."""

    coordinator = object.__new__(IstaDataUpdateCoordinator)
    coordinator._entry = DummyEntry(options={"URL": "dk_url"}, data={})
    coordinator.hass = DummyHass(base=".")
    coordinator.logger = coordinator_module._LOGGER
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


def test_set_controller_includes_url_from_options(monkeypatch: pytest.MonkeyPatch) -> None:
    """Coordinator should pass selected URL option to login_account for client selection."""

    coordinator = object.__new__(IstaDataUpdateCoordinator)
    coordinator.hass = DummyHass(base=".")
    coordinator._entry = DummyEntry(options={"URL": "dk_url"}, data={"email": "28523349853", "password": "secret"})

    captured: dict[str, Any] = {}

    def _fake_login_account(_hass: Any, data: dict[str, Any], _demo: bool = False) -> dict[str, Any]:
        captured.update(data)
        return {"controller": "dk"}

    monkeypatch.setattr(coordinator_module, "login_account", _fake_login_account)

    coordinator.set_controller()

    assert captured["URL"] == "dk_url"
    assert coordinator.controller == {"controller": "dk"}
