"""Binary sensors for weather-activities."""

import logging
import re

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONFID_NAME,
    CONFID_FORECAST_DAYS,
    ICON_ON,
    ICON_OFF,
)
from .coordinator import WeatherActivitiesDataCoordinator

LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the binary sensor platform."""
    LOGGER.debug("Setup new entry: %s", entry)
    
    forecast_days = entry.data.get(CONFID_FORECAST_DAYS)
    LOGGER.debug("Creating per-day sensors for %d days", forecast_days)
    
    coordinator: WeatherActivitiesDataCoordinator = hass.data[DOMAIN][entry.entry_id].coordinator
    
    async_add_entities([WeatherActivitiesSensor(entry=entry, coordinator=coordinator, day=day) for day in range(0,forecast_days)])

class WeatherActivitiesSensor(CoordinatorEntity, BinarySensorEntity):
    """Implementation of binary sensor."""

    def __init__(self, entry: ConfigEntry, coordinator: WeatherActivitiesDataCoordinator, day: int) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        
        self._entry = entry
        self._day = day
        
        name = self._entry.get(CONFID_NAME)
        key = name.sub(r'[-\s]+', '_', name).lower() + "_day_" + str(self._day)
        self.entity_description = BinarySensorEntityDescription(
            key=key,
            name=name + " Day " + str(self._day),
            icon=ICON_OFF,
            translation_key=DOMAIN + " perday",
        )

        self._attr_on = None
        self._attr_unique_id = f"{self._entry.entry_id}_{key}"

        LOGGER.debug("Initialized binary sensor for day %d from entry data: %s", day, self._entry.data)

    @property
    def device_info(self) -> DeviceInfo:
        """Get the device information."""
        return DeviceInfo(
            name=f"WeatherActivityPerDay{self.device.device_id}",
            manufacturer="HAExt",
            model="PerDay",
            sw_version="1.0",
            identifiers={
                (
                    DOMAIN,
                    f"{self.device.device_id}",
                )
            },
        )

    @property
    def is_on(self) -> bool:
        """Test if the entity is on."""
        return self._attr_on

    @property
    def available(self) -> bool:
        """Test if entity is available."""
        return self._attr_on is not None

    @property
    def icon(self) -> str:
        """Get the icon, based on the current state."""
        return ICON_ON if self.is_on else ICON_OFF

    @property
    def extra_state_attributes(self) -> dict:
        """Get state attributes."""
        return {}

    async def async_update(self) -> None:
        """Update the entity state."""
        self._attr_on = False
