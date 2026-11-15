"""Support for reading status from ecotrend-ista."""

from __future__ import annotations

from typing import Any, cast

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import EntityCategory
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


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Danish ista EcoTrend sensors."""
    coordinator: IstaDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([EcotrendDKSensor(coordinator, description, "dk") for description in DK_SENSOR_TYPES])
