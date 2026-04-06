"""Const for ista EcoTrend Version 3."""

from __future__ import annotations

from typing import Final

DOMAIN = "ecotrend_ista"
MANUFACTURER: Final = "Ista"
DEVICE_NAME: Final = "ista EcoTrend®"

DATA_HASS_CONFIG: Final = "hass_config"

TRACKER_UPDATE_STR: Final = f"{DOMAIN}_tracker_update"

# Deprecated config
CONF_UNIT = "unit"
CONF_UNIT_HEATING = "unit_heating"
CONF_UNIT_WARMWATER = "unit_warmwater"
CONF_YEARMONTH = "yearmonth"
CONF_YEAR = "year"
# Deprecated config

CONF_MFA = "mfa_code"

CONF_URL: Final = "URL"
CONF_UPDATE_INTERVAL: Final = "update_interval"

CONF_TYPE_HEATING: Final = "heating"
CONF_TYPE_HEATING_CASH: Final = "heating_costs"
CONF_TYPE_HEATING_CUSTOM: Final = "heating_custom"

CONF_TYPE_HEATWATER: Final = "warmwater"
CONF_TYPE_HEATWATER_CASH: Final = "warmwater_costs"
CONF_TYPE_HEATWATER_CUSTOM: Final = "warmwater_custom"

CONF_TYPE_WATER: Final = "water"
CONF_TYPE_WATER_CASH: Final = "water_costs"
CONF_TYPE_WATER_CUSTOM: Final = "water_custom"

# DK market types
CONF_TYPE_ELECTRICITY: Final = "electricity"
CONF_TYPE_ELECTRICITY_CONSUMPTION: Final = "electricity_consumption"
CONF_TYPE_ELECTRICITY_CONSUMPTION_DAY: Final = "electricity_consumption_day"
CONF_TYPE_ELECTRICITY_CONSUMPTION_WEEK: Final = "electricity_consumption_week"
CONF_TYPE_ELECTRICITY_CONSUMPTION_MONTH: Final = "electricity_consumption_month"
CONF_TYPE_ELECTRICITY_CONSUMPTION_YEAR: Final = "electricity_consumption_year"
CONF_TYPE_ELECTRICITY_CASH: Final = "electricity_costs"
CONF_TYPE_ELECTRICITY_CASH_DAY: Final = "electricity_costs_day"
CONF_TYPE_ELECTRICITY_CASH_BILLING: Final = "electricity_costs_billing"
CONF_TYPE_ELECTRICITY_CASH_WEEK: Final = "electricity_costs_week"
CONF_TYPE_ELECTRICITY_CASH_MONTH: Final = "electricity_costs_month"
CONF_TYPE_ELECTRICITY_CASH_YEAR: Final = "electricity_costs_year"

CONF_TYPE_HEATING_CONSUMPTION: Final = "heating_consumption"
CONF_TYPE_HEATING_CONSUMPTION_DAY: Final = "heating_consumption_day"
CONF_TYPE_HEATING_CONSUMPTION_WEEK: Final = "heating_consumption_week"
CONF_TYPE_HEATING_CONSUMPTION_MONTH: Final = "heating_consumption_month"
CONF_TYPE_HEATING_CONSUMPTION_YEAR: Final = "heating_consumption_year"
CONF_TYPE_HEATING_CASH_BILLING: Final = "heating_costs_billing"
CONF_TYPE_HEATING_CASH_DAY: Final = "heating_costs_day"
CONF_TYPE_HEATING_CASH_WEEK: Final = "heating_costs_week"
CONF_TYPE_HEATING_CASH_MONTH: Final = "heating_costs_month"
CONF_TYPE_HEATING_CASH_YEAR: Final = "heating_costs_year"
