"""Binary sensors for weather-activities."""

import datetime as dt
import logging
import re

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.components.weather import (
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TIME,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as hadt

from .const import (
    DOMAIN,
    CONFID_NAME,
    CONFID_FORECAST_DAYS,
    CONFID_TEMP_MIN,
    CONFID_TEMP_MAX,
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
    activity_name: str = entry.data.get(CONFID_NAME)
    device_info: DeviceInfo = DeviceInfo(
          name=f"WeatherActivity {activity_name}",
          manufacturer="HAExt",
          model="WeatherActivity",
          sw_version="1.0",
          identifiers={
              (
                  DOMAIN,
                  f"{activity_name}",
              )
          },
      )
    
    async_add_entities([WeatherActivitiesDaySensor(hass=hass, entry=entry, coordinator=coordinator, device_info=device_info, day=day) for day in range(0,forecast_days+1)])

class WeatherActivitiesSensor(CoordinatorEntity, BinarySensorEntity):
    """Implementation of binary sensor."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, coordinator: WeatherActivitiesDataCoordinator, device_info: DeviceInfo) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        
        self._attr_has_entity_name = True
        
        self._entry = entry
        self._device_info = device_info
        
        self._activity_name = self._entry.data.get(CONFID_NAME)
        self._name = self._generate_name()
        self._key = re.sub(r'[-\s]+', '_', self._name).lower()
        
        self.entity_id = generate_entity_id("binary_sensor.{}", DOMAIN + "_" + self._key, hass=hass)
        self.entity_description = BinarySensorEntityDescription(
            key=self._key,
            icon=ICON_OFF
        )

        self._load_from_coordinator()
        self._attr_unique_id = f"{self._entry.entry_id}_{self._key}"

        LOGGER.debug("Initialized binary sensor %s entry data: %s", self._name, self._entry.data)

    def _generate_name(self) -> str:
        """Generate a name for this entity"""
        return self._activity_name

    @property
    def device_info(self) -> DeviceInfo:
        """Get the device information."""
        return self._device_info

    @property
    def unique_id(self) -> str:
        """Get the unique id."""
        return f"{DOMAIN}-{self._key}"

    @property
    def name(self) -> str:
        """Get the entity name."""
        return self._name

    def _load_from_coordinator(self) -> None:
        if not self.coordinator.data.valid:
            LOGGER.debug("No valid coordinator data")
            self._attr_on = None
        else:
            forecasts = self.coordinator.data.forecasts
            self._load_from_forecasts(forecasts)
    
    def _load_from_forecasts(self, forecasts: list) -> None:
        LOGGER.debug("Not properly implemented")
        self._attr_on = None
    
    @callback
    def _handle_coordinator_update(self) -> None:
        """Update binary sensor with latest data from coordinator."""
        self._load_from_coordinator()
        self.async_write_ha_state()

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

class WeatherActivitiesDaySensor(WeatherActivitiesSensor):
    """Implementation of binary sensor for per-day."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, coordinator: WeatherActivitiesDataCoordinator, device_info: DeviceInfo, day: int) -> None:
        """Initialize the binary sensor."""
        self._day = day
        super().__init__(hass=hass, entry=entry, coordinator=coordinator, device_info=device_info)

    def _generate_name(self) -> str:
        """Generate a name for this entity"""
        return self._activity_name + " Day " + str(self._day)

    @property
    def translation_key(self) -> str:
        """Get the translation key."""
        return DOMAIN + " perday",

    @property
    def name(self) -> str:
        """Get the entity name."""
        return (hadt.now() + dt.timedelta(hours=24 * self._day)).strftime("%A") + " (+" + str(self._day) + "d)"

    def _load_from_forecasts(self, forecasts: list) -> None:
        forecasts = self.coordinator.data.forecasts
        filtered_time = self.filter_forecasts(forecasts)
        LOGGER.debug("Found forecasts in time range: %s", filtered_time)
        if (len(filtered_time) < 24) and (self._day > 0):
            LOGGER.debug("Found too few forecasts")
            self._attr_on = None
        else:
            temp_min = self._entry.data.get(CONFID_TEMP_MIN)
            temp_max = self._entry.data.get(CONFID_TEMP_MAX)
            LOGGER.debug("Filtering for temperatures between %s and %s", temp_min, temp_max)
            filtered_temp = [
                forecast
                for forecast in filtered_time
                if (((temp_max is None) or (forecast.get(ATTR_FORECAST_TEMP) < temp_max)) and ((temp_min is None) or (forecast.get(ATTR_FORECAST_TEMP) >= temp_min)))
            ]
            LOGGER.debug("Found forecasts in temp range: %s", filtered_temp)
            self._attr_on = len(filtered_temp) > 0
    
    def filter_forecasts(self, forecasts: list) -> list:
        """Filter forecasts down to those valid for this sensor."""
        now = hadt.now()
        time_start = hadt.start_of_local_day(now + dt.timedelta(hours=24 * self._day))
        time_end = hadt.start_of_local_day(now + dt.timedelta(hours=24 * (self._day + 1)))
        return [
            forecast
            for forecast in forecasts
            if (((time_forecast := hadt.parse_datetime(forecast.get(ATTR_FORECAST_TIME))) < time_end) and (time_forecast >= time_start))
        ]
