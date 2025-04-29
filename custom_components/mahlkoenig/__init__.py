"""Mahlkönig X54"""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import PLATFORMS
from .coordinator import MahlkonigUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a config entry."""

    # Do global setup
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    coordinator = MahlkonigUpdateCoordinator(hass, host, port)
    await coordinator.async_config_entry_first_refresh()

    if not coordinator.available:
        raise ConfigEntryNotReady(f"Mahlkönig X54 {host}:{port} is not available.")

    entry.runtime_data = coordinator

    # Forward the setup to your platform(s)
    # In this case it will forward it to sensor.py:async_setup_entry because PLATFORMS == ["sensor"]
    # See https://developers.home-assistant.io/docs/core/entity for available entities
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the sensor config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
