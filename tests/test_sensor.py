"""Tests for DK sensors."""

from __future__ import annotations

import asyncio
from typing import Any

from custom_components.ecotrend_ista.const import (
    CONF_TYPE_ELECTRICITY_CASH,
    CONF_TYPE_ELECTRICITY_CONSUMPTION,
    CONF_TYPE_HEATING_CASH_DAY,
    CONF_TYPE_HEATING_CONSUMPTION,
    DOMAIN,
)
from custom_components.ecotrend_ista.sensor import (
    DK_SENSOR_TYPES,
    EcotrendDKMeterSensor,
    EcotrendDKSensor,
    EcotrendDKSmokeSensor,
    EcotrendDKUserSettingsSensor,
    async_setup_entry,
)


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
                "electricity_costs_day": 12.0,
                "heating_consumption": 4.0,
                "heating_costs_day": 5.0,
                "electricity_unit": "kWh",
                "heat_unit": "Delinger",
                "currency_unit": "DKK",
                "user_info": {"Name": "DK User", "Language": "da-DK"},
                "user_settings": {
                    "Phone": "+4512345678",
                    "receiveNotification": True,
                    "receiveNotificationByPhone": True,
                    "receiveNotificationByMail": False,
                },
                "meters": [
                    {
                        "METER_ID": 123,
                        "METER_NO": "M-123",
                        "MeterText": "Electricity",
                        "MeterType": "EL",
                        "Unit": "kWh",
                        "ROOM_DESCR": "Kitchen",
                        "Reading_date": "2026-11-15",
                        "Last_Meter_Reading": 42,
                        "Last_Meter_Consumption": 5,
                        "Activation_date": "2020-01-01",
                        "Deactivation_date": "3000-01-01",
                    },
                    {
                        "METER_ID": 456,
                        "METER_NO": "M-456",
                        "MeterText": "Smoke",
                        "MeterType": "SMOKE",
                        "Unit": " ",
                        "ROOM_DESCR": "Hallway",
                        "Message": "Battery low",
                        "Headline": "Smoke detector status",
                        "smoke_status": "battery_low",
                        "Reading_date": "2026-11-15",
                        "Last_Meter_Reading": 0,
                        "Last_Meter_Consumption": 0,
                        "Activation_date": "2020-01-01",
                        "Deactivation_date": "3000-01-01",
                    },
                ],
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
    description = next(item for item in DK_SENSOR_TYPES if item.key == "electricity_costs_day")

    entity = EcotrendDKSensor(coordinator, description, "dk")

    assert entity.native_value == 12.0
    assert entity.native_unit_of_measurement == "DKK"
    assert entity.extra_state_attributes["user_info"]["Name"] == "DK User"


def test_dk_sensor_uses_meter_units() -> None:
    """Consumption sensor should use meter units from coordinator data."""

    entry = DummyConfigEntry()
    coordinator = DummyCoordinator(entry)
    description = next(item for item in DK_SENSOR_TYPES if item.key == "electricity_consumption")

    entity = EcotrendDKSensor(coordinator, description, "dk")

    assert entity.native_value == 8.0
    assert entity.native_unit_of_measurement == "kWh"


def test_dk_heat_sensors_resolve_values() -> None:
    """Heating consumption and economy sensors should map to DK payload keys."""

    entry = DummyConfigEntry()
    coordinator = DummyCoordinator(entry)

    heating_descr = next(item for item in DK_SENSOR_TYPES if item.key == CONF_TYPE_HEATING_CONSUMPTION)
    heat_economy_descr = next(item for item in DK_SENSOR_TYPES if item.key == CONF_TYPE_HEATING_CASH_DAY)

    heating_entity = EcotrendDKSensor(coordinator, heating_descr, "dk")
    heat_economy_entity = EcotrendDKSensor(coordinator, heat_economy_descr, "dk")

    assert heating_entity.native_value == 4.0
    assert heating_entity.native_unit_of_measurement == "Delinger"
    assert heat_economy_entity.native_value == 5.0
    assert heat_economy_entity.native_unit_of_measurement == "DKK"


def test_async_setup_entry_creates_dk_sensors() -> None:
    """DK setup should create one entity per DK sensor description."""

    entry = DummyConfigEntry()
    coordinator = DummyCoordinator(entry)
    hass = DummyHass(coordinator, entry)
    captured_entities: list[Any] = []

    def _add_entities(entities: list[Any]) -> None:
        captured_entities.extend(entities)

    asyncio.run(async_setup_entry(hass, entry, _add_entities))

    assert len(captured_entities) == len(DK_SENSOR_TYPES) + 4
    assert sum(isinstance(entity, EcotrendDKSensor) for entity in captured_entities) == len(DK_SENSOR_TYPES)
    assert sum(isinstance(entity, EcotrendDKMeterSensor) for entity in captured_entities) == 2
    assert sum(isinstance(entity, EcotrendDKSmokeSensor) for entity in captured_entities) == 1
    assert sum(isinstance(entity, EcotrendDKUserSettingsSensor) for entity in captured_entities) == 1
    assert {entity._attr_unique_id for entity in captured_entities if isinstance(entity, EcotrendDKSensor)} == {
        f"{item.key}_dk" for item in DK_SENSOR_TYPES
    }


def test_dk_meter_sensor_exposes_reading_and_metadata() -> None:
    """Meter diagnostic sensors should expose readings and identifying metadata."""

    entry = DummyConfigEntry()
    coordinator = DummyCoordinator(entry)
    meter = coordinator.data["dk"]["meters"][0]

    entity = EcotrendDKMeterSensor(coordinator, meter, 0)

    assert entity.native_value == 42
    assert entity.native_unit_of_measurement == "kWh"
    assert entity.extra_state_attributes["meter_type"] == "EL"
    assert entity.extra_state_attributes["room"] == "Kitchen"
    assert entity._attr_unique_id == "meter_123_last_reading"


def test_dk_smoke_sensor_exposes_normalized_status() -> None:
    """Smoke detector sensors should expose normalized status and raw metadata."""

    entry = DummyConfigEntry()
    coordinator = DummyCoordinator(entry)
    meter = coordinator.data["dk"]["meters"][1]

    entity = EcotrendDKSmokeSensor(coordinator, meter, 1)

    assert entity.native_value == "battery_low"
    assert entity.extra_state_attributes["headline"] == "Smoke detector status"
    assert entity._attr_unique_id == "meter_456_status"


def test_dk_user_settings_sensor_exposes_safe_phone_settings() -> None:
    """User settings sensor should expose notification state without the full phone number."""

    entry = DummyConfigEntry()
    coordinator = DummyCoordinator(entry)

    entity = EcotrendDKUserSettingsSensor(coordinator)

    assert entity.native_value == "enabled"
    assert entity.extra_state_attributes["phone_configured"] is True
    assert entity.extra_state_attributes["phone_last_four"] == "5678"
    assert "Phone" not in entity.extra_state_attributes
