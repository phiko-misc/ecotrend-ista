"""Support for reading status from ecotrend-ista."""

from __future__ import annotations

from typing import Any, cast

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_URL, DEVICE_NAME, DOMAIN, MANUFACTURER
from .const_schema import URL_SELECTORS
from .coordinator import IstaDataUpdateCoordinator
from .entity import DK_SENSOR_TYPES, DkSensorDescription


class EcotrendDKSensor(CoordinatorEntity[IstaDataUpdateCoordinator], SensorEntity):
    """Sensor entity class for ista EcoTrend DK."""

    _attr_force_update = False

    def __init__(
        self,
        coordinator: IstaDataUpdateCoordinator,
        description: DkSensorDescription,
        uuid: str,
    ) -> None:
        """Initialize the DK sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self.uuid = uuid
        self._attr_name = description.display_name.strip()
        self._attr_unique_id = f"{description.key}_{self.uuid}"
        self._attr_icon = description.icon
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class
        self._attr_entity_category = description.entity_category
        self._attr_attribution = f"Data provided by {URL_SELECTORS.get(self.coordinator.config_entry.options.get(CONF_URL))}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.uuid)},
            manufacturer=MANUFACTURER,
            model="ista DK consumption & costs",
            name=f"{DEVICE_NAME} DK",
        )

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of measurement for the DK sensor."""
        payload = (self.coordinator.data or {}).get(self.uuid, {})
        return payload.get(self.entity_description.unit_key)

    @property
    def native_value(self) -> StateType:
        """Return current DK sensor value."""
        payload = (self.coordinator.data or {}).get(self.uuid, {})
        return cast(StateType, payload.get(self.entity_description.key))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra DK sensor attributes."""
        payload = (self.coordinator.data or {}).get(self.uuid, {})
        return {"user_info": payload.get("user_info")}


class EcotrendDKMeterSensor(CoordinatorEntity[IstaDataUpdateCoordinator], SensorEntity):
    """Expose the latest reading and metadata for one DK meter."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:counter"

    def __init__(
        self,
        coordinator: IstaDataUpdateCoordinator,
        meter: dict[str, Any],
        index: int,
    ) -> None:
        """Initialize a meter diagnostic sensor."""
        super().__init__(coordinator)
        self._meter_key = str(meter.get("METER_ID") or meter.get("METER_NO") or index)
        self._initial_meter = meter
        meter_name = meter.get("MeterText") or meter.get("MeterType") or "Meter"
        self._attr_name = f"{meter_name} Last Reading"
        self._attr_unique_id = f"meter_{self._meter_key}_last_reading"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "dk")},
            manufacturer=MANUFACTURER,
            model="ista DK consumption & costs",
            name=f"{DEVICE_NAME} DK",
        )

    @property
    def _meter(self) -> dict[str, Any]:
        """Return the latest matching meter payload."""
        payload = (self.coordinator.data or {}).get("dk", {})
        for meter in payload.get("meters", []):
            meter_key = str(meter.get("METER_ID") or meter.get("METER_NO") or "")
            if meter_key == self._meter_key:
                return meter
        return self._initial_meter

    @property
    def native_value(self) -> StateType:
        """Return the latest meter reading."""
        return self._meter.get("Last_Meter_Reading")

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the meter unit."""
        unit = self._meter.get("Unit")
        return unit if isinstance(unit, str) and unit.strip() else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return identifying and lifecycle metadata for the meter."""
        meter = self._meter
        return {
            "meter_type": meter.get("MeterType"),
            "room": meter.get("ROOM_DESCR"),
            "meter_number": meter.get("METER_NO"),
            "reading_date": meter.get("Reading_date"),
            "last_consumption": meter.get("Last_Meter_Consumption"),
            "activation_date": meter.get("Activation_date"),
            "deactivation_date": meter.get("Deactivation_date"),
        }


class EcotrendDKSmokeSensor(CoordinatorEntity[IstaDataUpdateCoordinator], SensorEntity):
    """Expose the status message reported by a DK smoke detector."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:smoke-detector"

    def __init__(
        self,
        coordinator: IstaDataUpdateCoordinator,
        meter: dict[str, Any],
        index: int,
    ) -> None:
        """Initialize a smoke detector status sensor."""
        super().__init__(coordinator)
        self._meter_key = str(meter.get("METER_ID") or meter.get("METER_NO") or index)
        self._initial_meter = meter
        meter_name = meter.get("MeterText") or "Smoke detector"
        self._attr_name = f"{meter_name} Status"
        self._attr_unique_id = f"meter_{self._meter_key}_status"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "dk")},
            manufacturer=MANUFACTURER,
            model="ista DK consumption & costs",
            name=f"{DEVICE_NAME} DK",
        )

    @property
    def _meter(self) -> dict[str, Any]:
        """Return the latest matching smoke detector payload."""
        payload = (self.coordinator.data or {}).get("dk", {})
        for meter in payload.get("meters", []):
            meter_key = str(meter.get("METER_ID") or meter.get("METER_NO") or "")
            if meter_key == self._meter_key:
                return meter
        return self._initial_meter

    @property
    def native_value(self) -> str | None:
        """Return the raw smoke detector status reported by the API."""
        meter = self._meter
        for field in ("Message", "Headline"):
            status = meter.get(field)
            if isinstance(status, str) and status.strip():
                return status.strip()
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return smoke detector metadata and raw status fields."""
        meter = self._meter
        return {
            "meter_type": meter.get("MeterType"),
            "meter_number": meter.get("METER_NO"),
            "room": meter.get("ROOM_DESCR"),
            "message": meter.get("Message"),
            "headline": meter.get("Headline"),
            "reading_date": meter.get("Reading_date"),
            "activation_date": meter.get("Activation_date"),
            "deactivation_date": meter.get("Deactivation_date"),
        }


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Danish ista EcoTrend sensors."""
    coordinator: IstaDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    payload = (coordinator.data or {}).get("dk", {})
    meters = payload.get("meters", [])
    meter_entities = [
        EcotrendDKMeterSensor(coordinator, meter, index) for index, meter in enumerate(meters) if isinstance(meter, dict)
    ]
    smoke_entities = [
        EcotrendDKSmokeSensor(coordinator, meter, index)
        for index, meter in enumerate(meters)
        if isinstance(meter, dict) and meter.get("MeterType") == "SMOKE"
    ]
    async_add_entities(
        [EcotrendDKSensor(coordinator, description, "dk") for description in DK_SENSOR_TYPES] + meter_entities + smoke_entities
    )
