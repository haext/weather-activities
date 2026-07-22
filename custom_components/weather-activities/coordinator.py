"""Coordinator for weather-activities."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
)

LOGGER = logging.getLogger(__name__)

@dataclass
class CoordinatorData:
    """Class for the data held by the coorinator."""

class WeatherActivitiesDataCoordinator(DataUpdateCoordinator):
    """Coordinator to manage getting updates from the weather entity."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self._hass = hass
        self._entry = entry

        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN} ({self._entry.unique_id})"
            update_method=self.async_update_data,
        )

    async def async_update_data(self):
        """Fetch the data."""
        return CoordinatorData()

    async def custom_callback(self):
        """Callback from whatever is pushing data to this coordinator."""
        self.async_set_updated_data(CoordinatorData())
