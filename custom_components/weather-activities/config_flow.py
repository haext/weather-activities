from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries

from .const import (
    DOMAIN,
    CONFID_WEATHER_ENTITY,
    CONFID_FORECAST_DAYS,
    CONFDF_NAME,
    CONFDF_FORECAST_DAYS,
)

def get_config_data(entry: config_entries.ConfigEntry | None, key: str, default: Any = None) -> any:
    """Get data from a config entry, return the default if there is no entry."""
    if entry is None:
        return default
    return entry.data.get(key, default)

async def create_schema(config_entry: config_entries.ConfigEntry | None, hass: HomeAssistant,) -> vol.Schema:
    """Create the config flow schema."""
    
    # Get a list of the weather entities, and find a suggested entity if there's only one
    weather_entities = list(hass.states.async_entity_ids(WEATHER_DOMAIN))
    LOGGER.debug("Weather entities: %s", weather_entities)
    weather_entity = weather_entities[0] if weather_entities else None

    return vol.Schema(
        {
            vol.Required(CONFID_WEATHER_ENTITY, default=get_config_data(config_entry, CONFID_WEATHER_ENTITY, weather_entity)): selector(
                {
                    "entity": {
                        "include_entities": weather_entities,
                    },
                },
            ),
            vol.Optional(CONFID_FORECAST_DAYS, default=get_config_data(config_entry, CONFID_FORECAST_DAYS, CONFDF_FORECAST_DAYS)): vol.All(
                vol.Coerce(int), 
                vol.Range(min=1, max=21)
            ),
            vol.Optional(CONFID_TEMP_MIN, default=get_config_data(config_entry, CONFID_TEMP_MIN, CONFDF_TEMP_MIN)): vol.Coerce(float),
            vol.Optional(CONFID_TEMP_MAX, default=get_config_data(config_entry, CONFID_TEMP_MAX, CONFDF_TEMP_MAX)): vol.Coerce(float),
        },
    )


class WeatherActivitiesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for weather-activities."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONFDF_NAME], data=user_input)
        
        data_schema = await create_schema(config_entry=None, hass=self.hass)
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        errors = {}
        entry = self._get_reconfigure_entry() 
        
        if user_input is not None:
            return self.async_update_reload_and_abort(entry, data_updates={**entry.data, **user_input})
        
        data_schema = await create_schema(config_entry=entry, hass=self.hass)
        return self.async_show_form(step_id="reconfigure", data_schema=data_schema, errors=errors)
