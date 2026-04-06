"""Tests for the config flow helper utilities."""

from __future__ import annotations

import asyncio
from types import MappingProxyType
from typing import Any

import pytest

from custom_components.ecotrend_ista import config_flow
from custom_components.ecotrend_ista.config_flow import NotSupportedURL, validate_input, validate_options_input


class DummyHass:
    """Lightweight HomeAssistant stand-in for tests."""

    async def async_add_executor_job(self, func, *args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)


@pytest.fixture
def valid_user_input() -> dict[str, Any]:
    """Provide a baseline of valid user input values."""

    return {
        "email": "user@example.com",
        "password": "secret",
        "URL": "de_url",
        "mfa_code": "123456",
        "update_interval": 12,
    }


def test_validate_input_success(monkeypatch: pytest.MonkeyPatch, valid_user_input: dict[str, Any]) -> None:
    """A successful validation should return the title provided by the API client."""

    hass = DummyHass()

    class DummyAccount:
        def login(self) -> str:
            return "Demo"

        def get_support_code(self) -> str:
            return "SC123"

    def fake_login_account(_hass, data: MappingProxyType[str, Any], demo: bool = False) -> DummyAccount:
        assert demo is False
        assert data["email"] == valid_user_input["email"]
        return DummyAccount()

    monkeypatch.setattr(config_flow, "login_account", fake_login_account)

    result = asyncio.run(validate_input(hass, valid_user_input))

    assert result == {"title": "Ista SC123 Demo"}


def test_validate_input_rejects_unknown_url(valid_user_input: dict[str, Any]) -> None:
    """An unsupported URL value should raise NotSupportedURL."""

    hass = DummyHass()
    invalid_input = dict(valid_user_input)
    invalid_input["URL"] = "invalid"

    with pytest.raises(NotSupportedURL):
        asyncio.run(validate_input(hass, invalid_input))


def test_validate_input_accepts_dk_url(monkeypatch: pytest.MonkeyPatch, valid_user_input: dict[str, Any]) -> None:
    """DK URL should be accepted by validation."""

    hass = DummyHass()
    dk_input = dict(valid_user_input)
    dk_input["URL"] = "dk_url"

    class DummyAccount:
        def login(self) -> str:
            return "Authenticated"

        def get_user_info(self) -> dict[str, str]:
            return {"Username": "DK123"}

    monkeypatch.setattr(config_flow, "login_account", lambda *args, **kwargs: DummyAccount())

    result = asyncio.run(validate_input(hass, dk_input))

    assert result == {"title": "Ista DK123"}


def test_validate_input_accepts_dk_username_not_email(
    monkeypatch: pytest.MonkeyPatch, valid_user_input: dict[str, Any]
) -> None:
    """DK should accept account codes/usernames that are not email addresses."""

    hass = DummyHass()
    dk_input = dict(valid_user_input)
    dk_input["URL"] = "dk_url"
    dk_input["email"] = "0000000000000"

    class DummyAccount:
        def login(self) -> str:
            return "Authenticated"

        def get_user_info(self) -> dict[str, str]:
            return {"Username": "0000000000000"}

    monkeypatch.setattr(config_flow, "login_account", lambda *args, **kwargs: DummyAccount())

    result = asyncio.run(validate_input(hass, dk_input))

    assert result == {"title": "Ista 0000000000000"}


def test_validate_input_propagates_login_error(monkeypatch: pytest.MonkeyPatch, valid_user_input: dict[str, Any]) -> None:
    """Errors from the API login should bubble up for the flow to handle."""

    hass = DummyHass()

    class DummyAccount:
        def login(self) -> None:
            raise config_flow.LoginError("bad credentials")

    monkeypatch.setattr(config_flow, "login_account", lambda *args, **kwargs: DummyAccount())

    with pytest.raises(config_flow.LoginError):
        asyncio.run(validate_input(hass, valid_user_input))


def test_validate_options_input_returns_no_errors(valid_user_input: dict[str, Any]) -> None:
    """The option validation should accept the supported URL."""

    assert validate_options_input({"URL": "de_url"}) == {}
    assert validate_options_input({"URL": "dk_url"}) == {}


def test_validate_options_input_rejects_invalid_url() -> None:
    """An unsupported URL produces an error message."""

    assert validate_options_input({"URL": "other"}) == {"base": "not_allowed"}
