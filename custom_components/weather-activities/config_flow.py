from __future__ import annotations

import logging
import re
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.weather import (
    DOMAIN as DOMAIN_WEATHER,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import selector

from .const import (
    DOMAIN,
    CONFID_NAME,
    CONFID_WEATHER_ENTITY,
    CONFID_FORECAST_DAYS,
    CONFID_TEMP_MIN,
    CONFID_TEMP_MAX,
    CONFID_TIME_START,
    CONFID_TIME_END,
    CONFID_ISDAY_VALID,
    CONFID_ISDAY,
    CONFID_DOW,
    CONFID_HRS_MIN,
    CONFDF_NAME,
    CONFDF_FORECAST_DAYS,
    CONFDF_TEMP_MIN,
    CONFDF_TEMP_MAX,
    CONFDF_TIME_START,
    CONFDF_TIME_END,
    CONFDF_ISDAY_VALID,
    CONFDF_ISDAY,
    CONFDF_DOW,
    CONFDF_HRS_MIN,
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
            vol.Optional(CONFID_TIME_START, default=CONFDF_TIME_START): vol.Maybe(str),
            vol.Optional(CONFID_TIME_END, default=CONFDF_TIME_END): vol.Maybe(str),
            vol.Required(CONFID_ISDAY_VALID, default=CONFDF_ISDAY_VALID): bool,
            vol.Required(CONFID_ISDAY, default=CONFDF_ISDAY): bool,
            # vol.Optional(CONFID_DOW, default=CONFDF_DOW): vol.Maybe(str),
            vol.Optional(CONFID_HRS_MIN, default=CONFDF_HRS_MIN): vol.Maybe(vol.Coerce(int)),
        },
    )


class WeatherActivitiesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for weather-activities."""

    VERSION = 1
    MINOR_VERSION = 1
    
    dow_regex =  re.compile(r"^[MTWRFSU]+$")
    dow_msg = "Invalid day of week (use [MTWRFSU]+)"
    
    time_regex =  re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    time_msg = "Invalid time format (use HH:MM)"

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors = {}
        if user_input is not None:
            if user_input[CONFID_TIME_START] is not None and not self.time_regex.search(user_input[CONFID_TIME_START]):
                errors[CONFID_TIME_START] = self.time_msg
            if user_input[CONFID_TIME_END] is not None and not self.time_regex.search(user_input[CONFID_TIME_END]):
                errors[CONFID_TIME_END] = self.time_msg
            
            if not errors:
                return self.async_create_entry(title=user_input[CONFID_NAME], data=user_input)
        
        data_schema = await create_schema(hass=self.hass)
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        errors = {}
        entry = self._get_reconfigure_entry() 
        
        if user_input is not None:
            data_updates = {**entry.data, **user_input}
            
            if data_updates[CONFID_TIME_START] is not None and not self.time_regex.search(data_updates[CONFID_TIME_START]):
                errors[CONFID_TIME_START] = self.time_msg
            if data_updates[CONFID_TIME_END] is not None and not self.time_regex.search(data_updates[CONFID_TIME_END]):
                errors[CONFID_TIME_END] = self.time_msg
            
            if not errors:
                return self.async_update_reload_and_abort(entry, data_updates=data_updates)
        
        data_schema = self.add_suggested_values_to_schema(
            await create_schema(hass=self.hass), 
            entry.data
        )
        return self.async_show_form(step_id="reconfigure", data_schema=data_schema, errors=errors)
