"""Tests for DK sensors."""

from __future__ import annotations

import asyncio
from typing import Any

from custom_components.ecotrend_ista.const import DOMAIN
from custom_components.ecotrend_ista.sensor import DK_SENSOR_TYPES, EcotrendDKSensor, async_setup_entry


class DummyConfigEntry:
    """Simple config entry used for sensor setup tests."""

    def __init__(self, entry_id: str = "entry-dk") -> None:
        self.entry_id = entry_id
        self.options = {"URL": "dk_url"}


class DummyCoordinator:
    """Coordinator stand-in exposing the fields DK sensors use."""

    def __init__(self, config_entry: DummyConfigEntry) -> None:
        self.config_entry = config_entry
        self.data = {
            "dk": {
                "electricity_consumption": 8.0,
                "electricity_economy": 12.0,
                "heat_consumption": 4.0,
                "heat_economy": 5.0,
                "electricity_unit": "kWh",
                "heat_unit": "Delinger",
                "currency_unit": "kr",
                "user_info": {"Name": "DK User", "Language": "da-DK"},
            }
        }


class DummyHass:
    """Hass stand-in with only the data container used by async_setup_entry."""

    def __init__(self, coordinator: DummyCoordinator, entry: DummyConfigEntry) -> None:
        self.data = {DOMAIN: {entry.entry_id: coordinator}}


def test_dk_sensor_native_value_and_unit() -> None:
    """DK sensor should expose native value, unit, and user info attributes."""

    entry = DummyConfigEntry()
    coordinator = DummyCoordinator(entry)
    description = next(item for item in DK_SENSOR_TYPES if item.key == "electricity_economy")

    entity = EcotrendDKSensor(coordinator, description, "dk")

    assert entity.native_value == 12.0
    assert entity.native_unit_of_measurement == "kr"
    assert entity.extra_state_attributes["user_info"]["Name"] == "DK User"


def test_dk_sensor_uses_meter_units() -> None:
    """Consumption sensor should use meter units from coordinator data."""

    entry = DummyConfigEntry()
    coordinator = DummyCoordinator(entry)
    description = next(item for item in DK_SENSOR_TYPES if item.key == "electricity_consumption")

    entity = EcotrendDKSensor(coordinator, description, "dk")

    assert entity.native_value == 8.0
    assert entity.native_unit_of_measurement == "kWh"


def test_async_setup_entry_creates_dk_sensors() -> None:
    """DK setup should create one entity per DK sensor description."""

    entry = DummyConfigEntry()
    coordinator = DummyCoordinator(entry)
    hass = DummyHass(coordinator, entry)
    captured_entities: list[Any] = []

    def _add_entities(entities: list[Any]) -> None:
        captured_entities.extend(entities)

    asyncio.run(async_setup_entry(hass, entry, _add_entities))

    assert len(captured_entities) == len(DK_SENSOR_TYPES)
    assert all(isinstance(entity, EcotrendDKSensor) for entity in captured_entities)
    assert {entity._attr_unique_id for entity in captured_entities} == {
        "electricity_consumption_dk",
        "electricity_economy_dk",
        "heat_consumption_dk",
        "heat_economy_dk",
    }
