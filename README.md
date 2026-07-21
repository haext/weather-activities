# Weather Activities

[![GitHub Release][https://img.shields.io/github/v/release/haext/weather-activities?style=flat-square]][https://github.com/haext/weather-activities/releases/latest]
[![GitHub Downloads][https://img.shields.io/github/downloads/haext/weather-activities/total?style=flat-square]][https://github.com/haext/weather-activities/releases]
[![hacs][https://img.shields.io/badge/hacs-default-orange.svg?style=flat-square]][https://github.com/hacs/integration]

weather-activities is a HomeAssistant integration to identify when the forecasted weather is appropriate for outdoor activities.
Given a configured list of activities, and a weather entity, it will create a series of sensors to let you know when the weather is expected to be suitable for your activities.
This could be used, for example, to help plan when to wash a car, when the kids might want to swim in the pool, or when you'll want to open your windows for fresh air.

# Installation

[![Add to HACS via My Home Assistant][https://my.home-assistant.io/badges/hacs_repository.svg]][https://my.home-assistant.io/redirect/hacs_repository/?owner=haext&repository=weather-activities&category=integration]

Alternatively you may manually add this repository to HACS:

1. Navigate to `HACS` → `Integrations` → `...` (in the top right) → `Custom repositories`
2. Click `Add`
3. Paste `https://github.com/haext/weather-activities` into the `URL` field
4. Choose `Integration` as the `Category`
5. Search for `Weather Activities` in the integrations list, and then install it normally.

# Usage

1. [Configure](#configuration) a `weather-activities` device
2. Configure [activities](#activities) in your YAML configuration
3. Use the resulting `weather-activities` device entities for whatever you like

## Configuration

The configuration flow UI will allow you to set up a `weather-activities` device to monitor a specific [weather](https://www.home-assistant.io/integrations/weather/) entity's forecast data.
In addition, you must set the number of days of hourly forecast data to look at in order for the correct sensors to be created.

## Activities

For each activity you can configure:

| Field | Type | Description |
|-------|------|-------------|
| start | time | The earliest time of day at which this activity can start.  For example, I don't want to wash the car before 5am. If omitted, the activity may start at any time. |
| end | time | The latest time of day at which this activity can end.  For example, the kids aren't allowed to swim after 8pm, because that's bedtime.  If omitted, the activity may end at any time.  If the end time is less than the start time, the activity may wrap across midnight. |
| isday | bool | The activity may only take place during the day (`true`), night (`false`), or both (omitted). |
| temp_max | float | The maximum forecast temperature at which the activity is allowed. For example, I don't want to open the windows if the outside temperature is above 80F. |
| temp_min | float | The minimum forecast temperature at which the activity is allowed. For example, I don't want to go for a bike ride if the temperature is below 50F. |
| dow | string | The days of the week on which the activity is allowed.  Days are included by including the latter representing the day in this string (e.g. "MTWRFSU").  For example, I only want to hike on Saturday and Sunday. |

## Entities

| Sensor | Entity ID | Description |
|--------|-----------|-------------|
| Activity Allowed | `binary_sensor.<activity>_<day>` | Whether the activity is allowed `<day>` days in the future.  This sensors will have state attributes for the time ranges during the day in which the activity is allowed. |
| Activity Forecast | `binary_sensor.<activity>_forecast` | Whether the activity is forecast to be allowed on any upcoming day.  This sensor will have state attributes for the days on which the activity is expected to be allowed. |
| Activity Current | `binary_sensor.<activity>_current` | Whether the activity is currently allowed. |

# Related

* Similar integrations
  * [ha-check-weather](https://github.com/denysdovhan/ha-check-weather) - Excellent, but does not support multi-day per-hour forecasts
  * [ha-car_wash](https://github.com/Limych/ha-car_wash) - Far more restricted functionality

# License

[Apache-2.0](LICENSE)
