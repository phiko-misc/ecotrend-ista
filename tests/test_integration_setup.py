"""Integration setup and reload tests for DK mode."""

from __future__ import annotations

import asyncio
from typing import Any

from custom_components import ecotrend_ista as integration
from custom_components.ecotrend_ista.const import DOMAIN


class DummyEntry:
    """Config entry stand-in used for setup and reload tests."""

    def __init__(self, entry_id: str = "entry-dk") -> None:
        self.entry_id = entry_id
        self.options = {"URL": "dk_url"}
        self._update_listener: Any = None
        self._unload_callback: Any = None

    def add_update_listener(self, listener: Any):
        """Store listener and return an unsubscribe callback."""
        self._update_listener = listener
        return lambda: None

    def async_on_unload(self, callback: Any) -> None:
        """Store unload callback."""
        self._unload_callback = callback


class DummyConfigEntries:
    """Config entries manager stand-in for Home Assistant."""

    def __init__(self) -> None:
        self.forward_calls: list[tuple[Any, Any]] = []
        self.reload_calls: list[str] = []

    async def async_forward_entry_setups(self, entry: DummyEntry, platforms: list[Any]) -> None:
        """Track forwarded platform setup calls."""
        self.forward_calls.append((entry, platforms))

    async def async_reload(self, entry_id: str) -> None:
        """Track reload requests from the options listener."""
        self.reload_calls.append(entry_id)


class DummyHass:
    """Home Assistant stand-in used by integration setup tests."""

    def __init__(self) -> None:
        self.config_entries = DummyConfigEntries()
        self.data: dict[str, Any] = {}


class DummyCoordinator:
    """Coordinator stand-in to isolate setup lifecycle behavior."""

    instance_counter = 0

    def __init__(self, hass: DummyHass, entry: DummyEntry) -> None:
        self.hass = hass
        self.config_entry = entry
        self.controller = object()
        DummyCoordinator.instance_counter += 1
        self.instance_id = DummyCoordinator.instance_counter

    async def init(self) -> None:
        """No-op init hook."""

    async def async_config_entry_first_refresh(self) -> None:
        """No-op first refresh hook."""


async def _noop_migrate(*_args: Any, **_kwargs: Any) -> bool:
    return True


def test_options_update_listener_triggers_reload() -> None:
    """Updating options should request a config entry reload."""

    hass = DummyHass()
    entry = DummyEntry("entry-1")

    asyncio.run(integration.options_update_listener(hass, entry))

    assert hass.config_entries.reload_calls == ["entry-1"]


def test_dk_setup_and_reload_recreate_coordinator_without_migration(monkeypatch) -> None:
    """DK setup path should skip migration and replace coordinator on subsequent setup."""

    hass = DummyHass()
    entry = DummyEntry("entry-dk")
    migrate_calls: list[tuple[Any, ...]] = []

    async def _track_migrate(*args: Any, **kwargs: Any) -> bool:
        migrate_calls.append((*args, kwargs))
        return True

    monkeypatch.setattr(integration, "IstaDataUpdateCoordinator", DummyCoordinator)
    monkeypatch.setattr(integration, "_async_migrate_entries", _track_migrate)

    first_result = asyncio.run(integration.async_setup_entry(hass, entry))
    first_coordinator = hass.data[DOMAIN][entry.entry_id]

    second_result = asyncio.run(integration.async_setup_entry(hass, entry))
    second_coordinator = hass.data[DOMAIN][entry.entry_id]

    assert first_result is True
    assert second_result is True
    assert migrate_calls == []
    assert len(hass.config_entries.forward_calls) == 2
    assert first_coordinator is not second_coordinator
    assert first_coordinator.instance_id != second_coordinator.instance_id
