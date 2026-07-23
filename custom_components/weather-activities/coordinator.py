"""Coordinator for weather-activities."""

from dataclasses import dataclass
import logging

from homeassistant.components.weather import (
    DOMAIN as WEATHER_DOMAIN,
    SERVICE_GET_FORECASTS,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONFID_NAME,
    CONFID_WEATHER_ENTITY,
)

LOGGER = logging.getLogger(__name__)

@dataclass
class CoordinatorData:
    """Class for the data held by the coorinator."""
    
    valid: bool
    forecasts: list

class WeatherActivitiesDataCoordinator(DataUpdateCoordinator):
    """Coordinator to manage getting updates from the weather entity."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self._hass = hass
        self._entry = entry

        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN} ({self._entry.data.get(CONFID_NAME)})",
            update_method=self.get_coordinator_data,
        )
        
        self.unsubscribe = async_track_state_change_event(
            self.hass,
            [self._entry.data.get(CONFID_WEATHER_ENTITY)], 
            self._async_entity_state_changed
        )

    async def async_update_data(self):
        """Fetch the data."""
        return await self.get_coordinator_data()

    async def _async_entity_state_changed(self, event):
        """Update the coordinator data, because the entity state changed."""
        self.async_set_updated_data(await self.get_coordinator_data())

    async def get_coordinator_data(self) -> CoordinatorData:
        forecasts = await self.get_forecasts(self._entry.data.get(CONFID_WEATHER_ENTITY))
        return CoordinatorData(True, forecasts)

    async def get_forecasts(self, entity_id: str) -> list:
        """Get the forecasts from the weather entity."""
        weather_state = self.hass.states.get(entity_id)
        LOGGER.debug("Weather entity %s state: %s", entity_id, weather_state)

        if weather_state is None:
            raise UpdateFailed(f"Weather entity {entity_id} not found")

        entity_forecasts = await self.hass.services.async_call(
            domain=WEATHER_DOMAIN,
            service=SERVICE_GET_FORECASTS,
            service_data={
                "type": "hourly"
            },
            blocking=True,
            target={
                "entity_id": entity_id
            },
            return_response=True,
        )
        LOGGER.debug("Weather entity %s forecasts: %s", entity_id, entity_forecasts)
        forecasts = entity_forecasts.get(entity_id, {}).get("forecast", [])

        if forecasts is None:
            raise UpdateFailed(f"Failed to get forecasts from {entity_id}")

        return forecasts
