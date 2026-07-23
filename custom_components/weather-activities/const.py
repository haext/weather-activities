"""Constants for the weather-activities integration."""

from homeassistant.components.binary_sensor import (
    DOMAIN as DOMAIN_BINARY_SENSOR,
)

DOMAIN = "weather-activities"
PLATFORMS = [DOMAIN_BINARY_SENSOR]

# Configuration IDs
CONFID_NAME = "name"
CONFID_WEATHER_ENTITY = "weather_entity"
CONFID_FORECAST_DAYS = "forecast_days"
CONFID_TEMP_MIN = "temp_min"
CONFID_TEMP_MAX = "temp_max"
CONFID_TIME_START = "time_start"
CONFID_TIME_END = "time_end"
CONFID_ISDAY_VALID = "isday_valid"
CONFID_ISDAY = "isday"
CONFID_DOW = "dow"
CONFID_HRS_MIN = "hrs_min"

# Configuration Defaults
CONFDF_NAME = DOMAIN
CONFDF_FORECAST_DAYS = 7
CONFDF_TEMP_MIN = None
CONFDF_TEMP_MAX = None
CONFDF_TIME_START = None
CONFDF_TIME_END = None
CONFDF_ISDAY_VALID = False
CONFDF_ISDAY = None
CONFDF_DOW = None
CONFDF_HRS_MIN = None

# Icons
ICON_ON = "mdi:cloud-check-variant"
ICON_OFF = "mdi:cloud-alert"

# Attributes
ATTR_HRS_COUNT = "hrs_count"
ATTR_HRS_RANGES = "hrs_ranges"
ATTR_HRS_LIST = "hrs_list"
ATTR_DAYS_COUNT = "days_count"
ATTR_TEMP_MIN = "temp_min"
ATTR_TEMP_MAX = "temp_max"
