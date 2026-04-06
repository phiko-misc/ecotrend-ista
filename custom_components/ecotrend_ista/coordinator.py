"""Coordinator for ista EcoTrend Version 3."""

from __future__ import annotations

import datetime
from datetime import timedelta
import json
import logging
import os
from typing import Any

from pyecotrend_ista.helper_object_de import CustomRaw
from pyecotrend_ista.pyecotrend_ista import PyEcotrendIsta
try:
    from pyecotrend_ista.pyecotrend_ista_dk import PyEcotrendIstaDK
except ImportError:  # pragma: no cover - fallback for older library versions
    PyEcotrendIstaDK = Any  # type: ignore[assignment]
import requests

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .config_flow import login_account
from .const import CONF_UPDATE_INTERVAL, CONF_URL, DOMAIN
from .const import (
    CONF_TYPE_ELECTRICITY_CASH,
    CONF_TYPE_ELECTRICITY_CASH_DAY,
    CONF_TYPE_ELECTRICITY_CASH_BILLING,
    CONF_TYPE_ELECTRICITY_CASH_WEEK,
    CONF_TYPE_ELECTRICITY_CASH_MONTH,
    CONF_TYPE_ELECTRICITY_CASH_YEAR,
    CONF_TYPE_ELECTRICITY_CONSUMPTION,
    CONF_TYPE_ELECTRICITY_CONSUMPTION_DAY,
    CONF_TYPE_ELECTRICITY_CONSUMPTION_WEEK,
    CONF_TYPE_ELECTRICITY_CONSUMPTION_MONTH,
    CONF_TYPE_ELECTRICITY_CONSUMPTION_YEAR,
    CONF_TYPE_HEATING_CONSUMPTION,
    CONF_TYPE_HEATING_CONSUMPTION_DAY,
    CONF_TYPE_HEATING_CONSUMPTION_WEEK,
    CONF_TYPE_HEATING_CONSUMPTION_MONTH,
    CONF_TYPE_HEATING_CONSUMPTION_YEAR,
    CONF_TYPE_HEATING_CASH_DAY,
    CONF_TYPE_HEATING_CASH_BILLING,
    CONF_TYPE_HEATING_CASH_WEEK,
    CONF_TYPE_HEATING_CASH_MONTH,
    CONF_TYPE_HEATING_CASH_YEAR,
    CONF_TYPE_WATER_CASH,
)

_LOGGER = logging.getLogger(__name__)


async def create_directory_file(hass: HomeAssistant, consum_raw: CustomRaw, support_code: str):
    """Create a directory and a file with JSON content."""
    paths = [hass.config.path("www")]

    def mkdir() -> None:
        """Create directories if they do not exist."""
        for path in paths:
            if not os.path.exists(path):
                _LOGGER.debug("Creating directory: %s", path)
                os.makedirs(path, exist_ok=True)

    def make_file() -> None:
        """Create a JSON file with the data."""
        file_name = f"{DOMAIN}_{support_code}.json"
        media_path = hass.config.path("www")
        json_object = json.dumps(consum_raw.to_dict(), indent=4)
        with open(f"{media_path}/{file_name}", mode="w", encoding="utf-8") as f_lie:
            f_lie.write(json_object)

    await hass.async_add_executor_job(mkdir)
    await hass.async_add_executor_job(make_file)


class IstaDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator for ista EcoTrend Version 3."""

    controller: PyEcotrendIsta | PyEcotrendIstaDK

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
        """Set up the PyEcotrendIsta controller.

        This method initializes the PyEcotrendIsta controller instance with the provided email, password,
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
        return self._entry.options.get(CONF_URL, self._entry.data.get(CONF_URL, "de_url"))

    def _is_dk_url(self) -> bool:
        """Return whether this entry uses the DK backend."""
        return self._get_entry_url() == "dk_url"

    def get_uuids(self) -> list[str]:
        """Return available identifiers for entities.

        DE accounts expose multiple consumption UUIDs. DK currently uses one logical endpoint set,
        so we expose a synthetic single UUID.
        """
        if self._is_dk_url():
            return ["dk"]
        return self.controller.get_uuids()

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

        electricity_unit = (meter_types.get("electricity") or {}).get("unit")
        heat_unit = (meter_types.get("heat") or {}).get("unit")

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
                CONF_TYPE_WATER_CASH: self._extract_latest_numeric(heat_economy_day, "priceValue"),
                CONF_TYPE_HEATING_CASH_BILLING: self._extract_latest_numeric(heat_economy_billing, "priceValue"),
                CONF_TYPE_HEATING_CASH_WEEK: self._extract_latest_numeric(heat_economy_week, "priceValue"),
                CONF_TYPE_HEATING_CASH_MONTH: self._extract_latest_numeric(heat_economy_month, "priceValue"),
                CONF_TYPE_HEATING_CASH_YEAR: self._extract_latest_numeric(heat_economy_year, "priceValue"),
                "electricity_unit": electricity_unit,
                "heat_unit": heat_unit,
                "currency_unit": currency_unit,
                "user_info": user_info,
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
            if self._is_dk_url():
                self.data = await self.hass.async_add_executor_job(self._fetch_dk_data)
                self.logger.debug("Fetched DK data: %s", self.data)
                self.async_set_updated_data(self.data)
                return self.data

            for uuid in self.get_uuids():
                _consum_raw: dict[str, Any] = await self.hass.async_add_executor_job(
                    self.controller.consum_raw,
                    [
                        datetime.datetime.now().year,
                        datetime.datetime.now().year - 1,
                    ],
                    None,
                    True,
                    uuid,
                )
                if not isinstance(_consum_raw, dict):
                    return self.data[uuid]
                consum_raw: CustomRaw = CustomRaw.from_dict(_consum_raw)

                await create_directory_file(
                    self.hass,
                    consum_raw,
                    self.controller.get_support_code(),
                )
                self.data[uuid] = consum_raw
            self.async_set_updated_data(self.data)
            return self.data
        except requests.Timeout:
            pass
