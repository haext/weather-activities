from __future__ import annotations

import logging
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.weather import (
    DOMAIN as DOMAIN_WEATHER,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.selector import selector

from .const import (
    DOMAIN,
    CONFID_NAME,
    CONFID_WEATHER_ENTITY,
    CONFID_FORECAST_DAYS,
    CONFID_TEMP_MIN,
    CONFID_TEMP_MAX,
    CONFDF_NAME,
    CONFDF_FORECAST_DAYS,
    CONFDF_TEMP_MIN,
    CONFDF_TEMP_MAX,
)

LOGGER = logging.getLogger(__name__)

async def create_schema(hass: HomeAssistant) -> vol.Schema:
    """Create the config flow schema."""
    
    # Get a list of the weather entities, and find a suggested entity if there's only one
    weather_entities = list(hass.states.async_entity_ids(DOMAIN_WEATHER))
    LOGGER.debug("Weather entities: %s", weather_entities)
    weather_entity = weather_entities[0] if weather_entities else None

    return vol.Schema(
        {
            vol.Required(CONFID_NAME, default=CONFDF_NAME): str,
            vol.Required(CONFID_WEATHER_ENTITY, default=weather_entity): selector(
                {
                    "entity": {
                        "include_entities": weather_entities,
                    },
                },
            ),
            vol.Required(CONFID_FORECAST_DAYS, default=CONFDF_FORECAST_DAYS): vol.All(
                vol.Coerce(int), 
                vol.Range(min=1, max=21)
            ),
            vol.Optional(CONFID_TEMP_MIN, default=CONFDF_TEMP_MIN): vol.Maybe(vol.Coerce(float)),
            vol.Optional(CONFID_TEMP_MAX, default=CONFDF_TEMP_MAX): vol.Maybe(vol.Coerce(float)),
        },
    )


class WeatherActivitiesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for weather-activities."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONFID_NAME], data=user_input)
        
        data_schema = await create_schema(hass=self.hass)
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        errors = {}
        entry = self._get_reconfigure_entry() 
        
        if user_input is not None:
            return self.async_update_reload_and_abort(entry, data_updates={**entry.data, **user_input})
        
        data_schema = self.add_suggested_values_to_schema(
            await create_schema(hass=self.hass), 
            entry.data
        )
        return self.async_show_form(step_id="reconfigure", data_schema=data_schema, errors=errors)
