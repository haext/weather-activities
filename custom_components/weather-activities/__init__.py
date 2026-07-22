from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .coordinator import WeatherActivitiesDataCoordinator

LOGGER = logging.getLogger(__name__)

@dataclass
class RuntimeData:
    """Runtime data."""

    coordinator: WeatherActivitiesDataCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up weather-activities from a config entry."""
    LOGGER.info("Setup entry: %s", entry)
    hass.data.setdefault(DOMAIN, {})
    
    coordinator = WeatherActivitiesDataCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = RuntimeData(
        coordinator=coordinator
    )
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a weather-activities config entry."""
    LOGGER.info("Unload entry: %s", entry)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
