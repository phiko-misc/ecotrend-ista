"""Unofficial python library for the ista EcoTrend DK API."""

from __future__ import annotations

from http import HTTPStatus
import logging
from typing import Any, Literal, TypeAlias, cast

import requests

from .const import API_BASE_URL_DK, GRAPHS_API_BASE_URL_DK
from .exception_classes import LoginError, ParserError, ServerError
from .types import (
    ElectricityConsumptionResponse,
    MeterTypesResponse,
    MetersResponse,
    TokenResponse,
    UserInfo,
    UserSettings,
)

_LOGGER = logging.getLogger(__name__)

DkGraphMeterType: TypeAlias = Literal["Electricity", "Heat"]
DkGraphDataType: TypeAlias = Literal["Consumption", "Economy"]
DkGraphInterval: TypeAlias = Literal["billing", "day", "week", "month", "year"]
JsonDict: TypeAlias = dict[str, Any]
JsonList: TypeAlias = list[JsonDict]
JsonResponse: TypeAlias = JsonDict | JsonList

_VALID_METER_TYPES: tuple[str, ...] = ("Electricity", "Heat")
_VALID_DATA_TYPES: tuple[str, ...] = ("Consumption", "Economy")
_VALID_INTERVALS: tuple[str, ...] = ("billing", "day", "week", "month", "year")
_DK_CURRENCY_CODE: str = "DKK"
_INTERVAL_TO_VALUE: dict[DkGraphInterval, str] = {
    "day": "1",
    "week": "2",
    "month": "3",
    "year": "4",
    "billing": "5",
}


class PyEcotrendIstaDK:  # numpydoc ignore=PR01
    """Python client for interacting with the ista EcoTrend DK API."""

    _access_token: str | None = None
    _header: dict[str, str]

    def __init__(
        self,
        email: str,
        password: str,
        session: requests.Session | None = None,
    ) -> None:
        """Initialize the DK client."""
        self._email = email.strip()
        self._password = password
        self._header = {"User-Agent": self.get_user_agent()}
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": self.get_user_agent()})

    def _is_connected(self) -> bool:
        """Return whether a DK access token is available."""
        return bool(self._access_token)

    def get_user_agent(self) -> str:
        """Return the User-Agent string used for HTTP requests."""
        return (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0"
            " Safari/537.36"
        )

    def login(self) -> str | None:
        """Authenticate against the DK API and store an access token."""
        if self._is_connected():
            return self._access_token

        url = f"{API_BASE_URL_DK}token"
        payload = {
            "username": self._email,
            "password": self._password,
            "grant_type": "password",
        }

        try:
            with self.session.post(url, data=payload, headers=self._header) as response:
                _LOGGER.debug("Performed POST request: %s [%s]:\n%s", url, response.status_code, response.text)
                response.raise_for_status()
                try:
                    token = cast(TokenResponse, response.json())
                except requests.JSONDecodeError as exc:
                    raise ParserError("DK authentication failed due to an error parsing the request response") from exc
        except requests.HTTPError as exc:
            if exc.response.status_code == HTTPStatus.UNAUTHORIZED:
                raise LoginError("DK authentication failed due to an authorization failure") from exc
            raise ServerError(
                "DK authentication failed due to a server error "
                f"[{exc.response.status_code}: {exc.response.reason}]"
            ) from exc
        except requests.Timeout as exc:
            raise ServerError("DK authentication failed due a connection timeout") from exc
        except requests.RequestException as exc:
            raise ServerError("DK authentication failed due to a request exception") from exc

        self._access_token = token["access_token"]
        self._header["Authorization"] = f"Bearer {self._access_token}"
        return self._access_token

    def _get_dk(self, path: str) -> JsonResponse:
        """Perform authenticated GET requests against the DK base API."""
        self.login()
        url = f"{API_BASE_URL_DK}{path}"
        try:
            with self.session.get(url, headers=self._header) as response:
                _LOGGER.debug("Performed GET request: %s [%s]:\n%s", url, response.status_code, response.text)
                response.raise_for_status()
                try:
                    return response.json()
                except requests.JSONDecodeError as exc:
                    raise ParserError(f"Loading DK data for '{path}' failed due to an error parsing the request response") from exc
        except requests.HTTPError as exc:
            if exc.response.status_code == HTTPStatus.UNAUTHORIZED:
                raise LoginError(f"Loading DK data for '{path}' failed due to an authorization failure") from exc
            raise ServerError(
                f"Loading DK data for '{path}' failed due to a server error "
                f"[{exc.response.status_code}: {exc.response.reason}]"
            ) from exc
        except requests.Timeout as exc:
            raise ServerError(f"Loading DK data for '{path}' failed due a connection timeout") from exc
        except requests.RequestException as exc:
            raise ServerError(f"Loading DK data for '{path}' failed due to a request exception") from exc

    def _get_dk_graph(self, path: str) -> JsonResponse:
        """Perform authenticated GET requests against the DK graphs API."""
        self.login()
        url = f"{GRAPHS_API_BASE_URL_DK}{path}"
        try:
            with self.session.get(url, headers=self._header) as response:
                _LOGGER.debug("Performed GET request: %s [%s]:\n%s", url, response.status_code, response.text[:200])
                response.raise_for_status()
                try:
                    return response.json()
                except requests.JSONDecodeError as exc:
                    raise ParserError(
                        f"Loading DK graph data for '{path}' failed due to an error parsing the request response"
                    ) from exc
        except requests.HTTPError as exc:
            if exc.response.status_code == HTTPStatus.UNAUTHORIZED:
                raise LoginError(f"Loading DK graph data for '{path}' failed due to an authorization failure") from exc
            raise ServerError(
                f"Loading DK graph data for '{path}' failed due to a server error "
                f"[{exc.response.status_code}: {exc.response.reason}]"
            ) from exc
        except requests.Timeout as exc:
            raise ServerError(f"Loading DK graph data for '{path}' failed due a connection timeout") from exc
        except requests.RequestException as exc:
            raise ServerError(f"Loading DK graph data for '{path}' failed due to a request exception") from exc

    def get_user_info(self) -> UserInfo:
        """Return user information from the DK API."""
        return cast(UserInfo, self._get_dk("api/GetUserInfo"))

    def get_user_settings(self) -> UserSettings:
        """Return user settings from the DK API."""
        return cast(UserSettings, self._get_dk("api/GetUserSettings"))

    def get_meters(self) -> MetersResponse:
        """Return meter information from the DK API."""
        return cast(MetersResponse, self._get_dk("api/Meters"))

    def get_meter_types(self) -> MeterTypesResponse:
        """Return available meter types from the DK graphs API."""
        return cast(MeterTypesResponse, self._get_dk_graph("MeterType/GetMeterTypes"))

    def get_currency_code(self) -> str:
        """Return DK ISO 4217 currency code used for economy values."""
        return _DK_CURRENCY_CODE

    def get_graph_data(
        self,
        meter_type: DkGraphMeterType,
        data_type: DkGraphDataType,
        interval: DkGraphInterval,
    ) -> ElectricityConsumptionResponse:
        """Return DK graph values for meter type, dataset type, and interval."""
        if meter_type not in _VALID_METER_TYPES:
            raise ValueError(f"Invalid meter_type '{meter_type}'. Allowed values: {_VALID_METER_TYPES}")
        if data_type not in _VALID_DATA_TYPES:
            raise ValueError(f"Invalid data_type '{data_type}'. Allowed values: {_VALID_DATA_TYPES}")
        if interval not in _VALID_INTERVALS:
            raise ValueError(f"Invalid interval '{interval}'. Allowed values: {_VALID_INTERVALS}")

        interval_value = _INTERVAL_TO_VALUE[interval]

        # Keep endpoint/query naming exactly as defined in the Postman Ista collection.
        if meter_type == "Heat" and data_type == "Economy":
            path = f"Overview/Economy_Heat_Data?inverval={interval_value}"
        elif meter_type == "Heat" and data_type == "Consumption":
            path = f"Overview/Usage_Heat_Data?inverval={interval_value}"
        elif meter_type == "Electricity" and data_type == "Economy":
            path = f"Overview/Economy_Electricity_Data?inverval={interval_value}"
        else:
            path = f"Overview/Usage_Electricity_Data?interval={interval_value}"

        return cast(ElectricityConsumptionResponse, self._get_dk_graph(path))

    def get_electricity_consumption(
        self,
        interval: DkGraphInterval,
    ) -> ElectricityConsumptionResponse:
        """Return electricity consumption graph values for the selected interval."""
        return self.get_graph_data("Electricity", "Consumption", interval)

    def get_electricity_economy(
        self,
        interval: DkGraphInterval,
    ) -> ElectricityConsumptionResponse:
        """Return electricity economy graph values for the selected interval."""
        return self.get_graph_data("Electricity", "Economy", interval)

    def get_heat_consumption(
        self,
        interval: DkGraphInterval,
    ) -> ElectricityConsumptionResponse:
        """Return heat consumption graph values for the selected interval."""
        return self.get_graph_data("Heat", "Consumption", interval)

    def get_heat_economy(
        self,
        interval: DkGraphInterval,
    ) -> ElectricityConsumptionResponse:
        """Return heat economy graph values for the selected interval."""
        return self.get_graph_data("Heat", "Economy", interval)

    def get_electricity_consumption_billing(self) -> ElectricityConsumptionResponse:
        """Return electricity consumption graph data for billing interval."""
        return self.get_electricity_consumption("billing")

    def get_electricity_consumption_day(self) -> ElectricityConsumptionResponse:
        """Return electricity consumption graph data for day interval."""
        return self.get_electricity_consumption("day")

    def get_electricity_consumption_week(self) -> ElectricityConsumptionResponse:
        """Return electricity consumption graph data for week interval."""
        return self.get_electricity_consumption("week")

    def get_electricity_consumption_month(self) -> ElectricityConsumptionResponse:
        """Return electricity consumption graph data for month interval."""
        return self.get_electricity_consumption("month")

    def get_electricity_consumption_year(self) -> ElectricityConsumptionResponse:
        """Return electricity consumption graph data for year interval."""
        return self.get_electricity_consumption("year")

    def get_electricity_economy_billing(self) -> ElectricityConsumptionResponse:
        """Return electricity economy graph data for billing interval."""
        return self.get_electricity_economy("billing")

    def get_electricity_economy_day(self) -> ElectricityConsumptionResponse:
        """Return electricity economy graph data for day interval."""
        return self.get_electricity_economy("day")

    def get_electricity_economy_week(self) -> ElectricityConsumptionResponse:
        """Return electricity economy graph data for week interval."""
        return self.get_electricity_economy("week")

    def get_electricity_economy_month(self) -> ElectricityConsumptionResponse:
        """Return electricity economy graph data for month interval."""
        return self.get_electricity_economy("month")

    def get_electricity_economy_year(self) -> ElectricityConsumptionResponse:
        """Return electricity economy graph data for year interval."""
        return self.get_electricity_economy("year")

    def get_heat_consumption_billing(self) -> ElectricityConsumptionResponse:
        """Return heat consumption graph data for billing interval."""
        return self.get_heat_consumption("billing")

    def get_heat_consumption_day(self) -> ElectricityConsumptionResponse:
        """Return heat consumption graph data for day interval."""
        return self.get_heat_consumption("day")

    def get_heat_consumption_week(self) -> ElectricityConsumptionResponse:
        """Return heat consumption graph data for week interval."""
        return self.get_heat_consumption("week")

    def get_heat_consumption_month(self) -> ElectricityConsumptionResponse:
        """Return heat consumption graph data for month interval."""
        return self.get_heat_consumption("month")

    def get_heat_consumption_year(self) -> ElectricityConsumptionResponse:
        """Return heat consumption graph data for year interval."""
        return self.get_heat_consumption("year")

    def get_heat_economy_billing(self) -> ElectricityConsumptionResponse:
        """Return heat economy graph data for billing interval."""
        return self.get_heat_economy("billing")

    def get_heat_economy_day(self) -> ElectricityConsumptionResponse:
        """Return heat economy graph data for day interval."""
        return self.get_heat_economy("day")

    def get_heat_economy_week(self) -> ElectricityConsumptionResponse:
        """Return heat economy graph data for week interval."""
        return self.get_heat_economy("week")

    def get_heat_economy_month(self) -> ElectricityConsumptionResponse:
        """Return heat economy graph data for month interval."""
        return self.get_heat_economy("month")

    def get_heat_economy_year(self) -> ElectricityConsumptionResponse:
        """Return heat economy graph data for year interval."""
        return self.get_heat_economy("year")