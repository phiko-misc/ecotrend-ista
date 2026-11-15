"""Coordinator for ista EcoTrend Version 3."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

try:
    from pyecotrend_ista.pyecotrend_ista_dk import PyEcotrendIstaDK
except ImportError:  # pragma: no cover - fallback for older library versions
    PyEcotrendIstaDK = Any  # type: ignore[assignment]
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
import requests

from .config_flow import login_account
from .const import (
    CONF_TYPE_ELECTRICITY_CASH,
    CONF_TYPE_ELECTRICITY_CASH_BILLING,
    CONF_TYPE_ELECTRICITY_CASH_DAY,
    CONF_TYPE_ELECTRICITY_CASH_MONTH,
    CONF_TYPE_ELECTRICITY_CASH_WEEK,
    CONF_TYPE_ELECTRICITY_CASH_YEAR,
    CONF_TYPE_ELECTRICITY_CONSUMPTION,
    CONF_TYPE_ELECTRICITY_CONSUMPTION_DAY,
    CONF_TYPE_ELECTRICITY_CONSUMPTION_MONTH,
    CONF_TYPE_ELECTRICITY_CONSUMPTION_WEEK,
    CONF_TYPE_ELECTRICITY_CONSUMPTION_YEAR,
    CONF_TYPE_HEATING_CASH_BILLING,
    CONF_TYPE_HEATING_CASH_DAY,
    CONF_TYPE_HEATING_CASH_MONTH,
    CONF_TYPE_HEATING_CASH_WEEK,
    CONF_TYPE_HEATING_CASH_YEAR,
    CONF_TYPE_HEATING_CONSUMPTION,
    CONF_TYPE_HEATING_CONSUMPTION_DAY,
    CONF_TYPE_HEATING_CONSUMPTION_MONTH,
    CONF_TYPE_HEATING_CONSUMPTION_WEEK,
    CONF_TYPE_HEATING_CONSUMPTION_YEAR,
    CONF_UPDATE_INTERVAL,
    CONF_URL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class IstaDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator for ista EcoTrend Version 3."""

    controller: PyEcotrendIstaDK

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize ista EcoTrend Version 3 data updater."""
        self._entry = entry
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=f"{DOMAIN}-{entry.entry_id}",
            update_method=self._async_update_data,
            update_interval=timedelta(hours=self._entry.options.get(CONF_UPDATE_INTERVAL, 24)),
        )

    def set_controller(self) -> None:
        """Set up the Danish PyEcotrendIsta controller.

        This method initializes the controller with the provided username and password,
        and other necessary configurations.
        """
        data = {
            **self._entry.data,
            CONF_URL: self._get_entry_url(),
        }
        self.controller = login_account(
            self.hass,
            data,
            self._entry.options.get("dev_demo", False),
        )

    def _get_entry_url(self) -> str:
        """Return the selected login URL key for this entry."""
        return self._entry.options.get(CONF_URL, self._entry.data.get(CONF_URL, "dk_url"))

    def _is_dk_url(self) -> bool:
        """Return whether this entry uses the DK backend."""
        return self._get_entry_url() == "dk_url"

    def get_uuids(self) -> list[str]:
        """Return available identifiers for entities.

        DK uses one logical endpoint set, so we expose a synthetic single UUID.
        """
        return ["dk"]

    @staticmethod
    def _extract_latest_numeric(records: Any, field: str) -> float | None:
        """Return the latest non-null numeric value from a DK graph response list."""
        if not isinstance(records, list):
            return None
        for item in reversed(records):
            if not isinstance(item, dict):
                continue
            value = item.get(field)
            if isinstance(value, (int, float)):
                return float(value)
        return None

    def _safe_dk_call(self, method_name: str, default: Any) -> Any:
        """Call a DK controller method safely and return default on failure."""
        method = getattr(self.controller, method_name, None)
        if method is None:
            return default

        try:
            return method()
        except Exception as error:  # pylint: disable=broad-except
            _LOGGER.warning("DK endpoint '%s' failed: %s", method_name, error)
            return default

    @staticmethod
    def _normalize_smoke_status(meter: dict[str, Any]) -> str:
        """Normalize a smoke meter message into a stable status."""
        raw_status = " ".join(
            str(meter.get(field, "")).strip() for field in ("Message", "Headline") if meter.get(field)
        ).lower()
        if not raw_status:
            return "unknown"
        if any(term in raw_status for term in ("alarm", "fire", "røg", "smoke")):
            return "alarm"
        if any(term in raw_status for term in ("battery", "batteri")):
            return "battery_low"
        if any(term in raw_status for term in ("fault", "error", "fejl")):
            return "fault"
        if any(term in raw_status for term in ("tamper", "sabotage")):
            return "tamper"
        if any(term in raw_status for term in ("test", "prøve")):
            return "test"
        if any(term in raw_status for term in ("clear", "normal", "ok", "ingen")):
            return "clear"
        return "unknown"

    @classmethod
    def _normalize_meters(cls, meters: list[Any]) -> list[dict[str, Any]]:
        """Normalize meter records for Home Assistant entities."""
        normalized_meters = []
        for meter in meters:
            if not isinstance(meter, dict):
                continue
            normalized_meter = dict(meter)
            if str(normalized_meter.get("MeterType", "")).upper() == "SMOKE":
                normalized_meter["smoke_status"] = cls._normalize_smoke_status(normalized_meter)
            normalized_meters.append(normalized_meter)
        return normalized_meters

    def _fetch_dk_data(self) -> dict[str, dict[str, Any]]:
        """Fetch the DK data shape used by DK sensor entities."""
        meter_types = self._safe_dk_call("get_meter_types", {})
        currency_unit = self._safe_dk_call("get_currency_code", "DKK")

        # Electricity consumption
        electricity_consumption_billing = self._safe_dk_call("get_electricity_consumption_billing", [])
        electricity_consumption_day = self._safe_dk_call("get_electricity_consumption_day", [])
        electricity_consumption_week = self._safe_dk_call("get_electricity_consumption_week", [])
        electricity_consumption_month = self._safe_dk_call("get_electricity_consumption_month", [])
        electricity_consumption_year = self._safe_dk_call("get_electricity_consumption_year", [])

        # Electricity costs
        electricity_economy_day = self._safe_dk_call("get_electricity_economy_day", [])
        electricity_economy_billing = self._safe_dk_call("get_electricity_economy_billing", [])
        electricity_economy_week = self._safe_dk_call("get_electricity_economy_week", [])
        electricity_economy_month = self._safe_dk_call("get_electricity_economy_month", [])
        electricity_economy_year = self._safe_dk_call("get_electricity_economy_year", [])

        # Heat consumption
        heat_consumption_billing = self._safe_dk_call("get_heat_consumption_billing", [])
        heat_consumption_day = self._safe_dk_call("get_heat_consumption_day", [])
        heat_consumption_week = self._safe_dk_call("get_heat_consumption_week", [])
        heat_consumption_month = self._safe_dk_call("get_heat_consumption_month", [])
        heat_consumption_year = self._safe_dk_call("get_heat_consumption_year", [])

        # Heat costs
        heat_economy_day = self._safe_dk_call("get_heat_economy_day", [])
        heat_economy_billing = self._safe_dk_call("get_heat_economy_billing", [])
        heat_economy_week = self._safe_dk_call("get_heat_economy_week", [])
        heat_economy_month = self._safe_dk_call("get_heat_economy_month", [])
        heat_economy_year = self._safe_dk_call("get_heat_economy_year", [])

        user_info = self._safe_dk_call("get_user_info", {})
        meters_response = self._safe_dk_call("get_meters", {})
        meters = []
        if isinstance(meters_response, dict):
            meter_container = meters_response.get("Meters", {})
            if isinstance(meter_container, dict):
                meter_values = meter_container.get("Value", meter_container.get("value", []))
                if isinstance(meter_values, list):
                    meters = self._normalize_meters(meter_values)

        electricity_unit = (meter_types.get("electricity") or {}).get("unit")
        heat_unit = (meter_types.get("heat") or {}).get("unit")
        user_settings = self._safe_dk_call("get_user_settings", {})

        return {
            "dk": {
                CONF_TYPE_ELECTRICITY_CONSUMPTION: self._extract_latest_numeric(electricity_consumption_billing, "value"),
                CONF_TYPE_ELECTRICITY_CONSUMPTION_DAY: self._extract_latest_numeric(electricity_consumption_day, "value"),
                CONF_TYPE_ELECTRICITY_CONSUMPTION_WEEK: self._extract_latest_numeric(electricity_consumption_week, "value"),
                CONF_TYPE_ELECTRICITY_CONSUMPTION_MONTH: self._extract_latest_numeric(electricity_consumption_month, "value"),
                CONF_TYPE_ELECTRICITY_CONSUMPTION_YEAR: self._extract_latest_numeric(electricity_consumption_year, "value"),
                CONF_TYPE_ELECTRICITY_CASH_DAY: self._extract_latest_numeric(electricity_economy_day, "priceValue"),
                CONF_TYPE_ELECTRICITY_CASH: self._extract_latest_numeric(electricity_economy_day, "priceValue"),
                CONF_TYPE_ELECTRICITY_CASH_BILLING: self._extract_latest_numeric(electricity_economy_billing, "priceValue"),
                CONF_TYPE_ELECTRICITY_CASH_WEEK: self._extract_latest_numeric(electricity_economy_week, "priceValue"),
                CONF_TYPE_ELECTRICITY_CASH_MONTH: self._extract_latest_numeric(electricity_economy_month, "priceValue"),
                CONF_TYPE_ELECTRICITY_CASH_YEAR: self._extract_latest_numeric(electricity_economy_year, "priceValue"),
                CONF_TYPE_HEATING_CONSUMPTION: self._extract_latest_numeric(heat_consumption_billing, "value"),
                CONF_TYPE_HEATING_CONSUMPTION_DAY: self._extract_latest_numeric(heat_consumption_day, "value"),
                CONF_TYPE_HEATING_CONSUMPTION_WEEK: self._extract_latest_numeric(heat_consumption_week, "value"),
                CONF_TYPE_HEATING_CONSUMPTION_MONTH: self._extract_latest_numeric(heat_consumption_month, "value"),
                CONF_TYPE_HEATING_CONSUMPTION_YEAR: self._extract_latest_numeric(heat_consumption_year, "value"),
                CONF_TYPE_HEATING_CASH_DAY: self._extract_latest_numeric(heat_economy_day, "priceValue"),
                CONF_TYPE_HEATING_CASH_BILLING: self._extract_latest_numeric(heat_economy_billing, "priceValue"),
                CONF_TYPE_HEATING_CASH_WEEK: self._extract_latest_numeric(heat_economy_week, "priceValue"),
                CONF_TYPE_HEATING_CASH_MONTH: self._extract_latest_numeric(heat_economy_month, "priceValue"),
                CONF_TYPE_HEATING_CASH_YEAR: self._extract_latest_numeric(heat_economy_year, "priceValue"),
                "electricity_unit": electricity_unit,
                "heat_unit": heat_unit,
                "currency_unit": currency_unit,
                "user_info": user_info,
                "user_settings": user_settings,
                "meters": meters,
            }
        }

    async def init(self) -> None:
        """Initialize the controller and perform the login."""
        self.set_controller()
        await self.hass.async_add_executor_job(self.controller.login)

    async def _async_update_data(self):
        """Update the data from ista EcoTrend Version 3."""
        try:
            if self.data is None:
                self.data = {}
            await self.init()
            self.data = await self.hass.async_add_executor_job(self._fetch_dk_data)
            self.logger.debug("Fetched DK data: %s", self.data)
            self.async_set_updated_data(self.data)
            return self.data
        except requests.Timeout:
            pass
