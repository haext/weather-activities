# Weather Activities

[![GitHub Release](https://img.shields.io/github/v/release/haext/weather-activities?style=flat-square)](https://github.com/haext/weather-activities/releases/latest)
[![GitHub Downloads](https://img.shields.io/github/downloads/haext/weather-activities/total?style=flat-square)](https://github.com/haext/weather-activities/releases)
[![hacs](https://img.shields.io/badge/hacs-default-orange.svg?style=flat-square)](https://github.com/hacs/integration)

weather-activities is a HomeAssistant integration to identify when the forecasted weather is appropriate for outdoor activities.
Given a configured list of activities, and a weather entity, it will create a series of sensors to let you know when the weather is expected to be suitable for your activities.
This could be used, for example, to help plan when to wash a car, when the kids might want to swim in the pool, or when you'll want to open your windows for fresh air.

# Installation

[![Add to HACS via My Home Assistant](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=haext&repository=weather-activities&category=integration)

Alternatively you may manually add this repository to HACS:

1. Navigate to `HACS` → `Integrations` → `...` (in the top right) → `Custom repositories`
2. Click `Add`
3. Paste `https://github.com/haext/weather-activities` into the `URL` field
4. Choose `Integration` as the `Category`
5. Search for `Weather Activities` in the integrations list, and then install it normally.

# Usage

## Configuration

Each weather `weather-activities` represents a specific activity you're interested in, which depends on the weather.
For each activity, you will configure an instance of this integration to monitor a specific [weather](https://www.home-assistant.io/integrations/weather/) entity's forecast data for a specified number of days in the future.

For each activity you can configure:

| Field | Type | Description |
|-------|------|-------------|
| start | time | The earliest time of day at which this activity can start.  For example, I don't want to wash the car before 5am. If omitted, the activity may start at any time. |
| end | time | The latest time of day at which this activity can end.  For example, the kids aren't allowed to swim after 8pm, because that's bedtime.  If omitted, the activity may end at any time.  If the end time is less than the start time, the activity may wrap across midnight. |
| isday_valid | bool | Whether this activity depends on it being day or not.  If not checked the `isday` field below will be ignored. |
| isday | bool | The activity may only take place during the day (`true`/`checked`) or night (`false`/`unchecked`). |
| temp_max | float | The maximum forecast temperature at which the activity is allowed. For example, I don't want to open the windows if the outside temperature is above 80F. |
| temp_min | float | The minimum forecast temperature at which the activity is allowed. For example, I don't want to go for a bike ride if the temperature is below 50F. |
| dow | string | The days of the week on which the activity is allowed.  Days are included by including the latter representing the day in this string (e.g. "MTWRFSU").  For example, I only want to hike on Saturday and Sunday. |

## Entities

| Sensor | Entity ID | Description |
|--------|-----------|-------------|
| Activity | `binary_sensor.weather_activities_<activity>` | Whether the activity is forecast to be possible on any upcoming day. |
| Day | `binary_sensor.weather_activities_<activity>_day_<day>` | Whether the activity could happen `<day>` days in the future.  These sensors have state attributes for the time ranges during the day in which the activity can happen. Note that these sensors names will change to include the date, day of the week, and how many days ahead, but the underlying `entity_id` includes only how many days in the future. |

## UI

By combining the [auto-entities](https://github.com/thomasloven/lovelace-auto-entities) and [multiple-entity-row](https://github.com/benct/lovelace-multiple-entity-row), it is possible to create a GUI list of all the days when an activity is forecast to be possible.

First, create `weather_activities.jinja` as a [custom jinja template](https://www.home-assistant.io/docs/templating/custom-templates/) with the following contents:

```
{%- macro weather_activities_entities(primary_entity) -%}
  {%- set entities = device_entities(device_id(primary_entity)) -%}
  {%- set ns = namespace(dicts=[]) -%}
  
  {%- for entity in entities -%}
    {%- if entity | regex_match('.*\d+') -%}
      {%- set ns.dicts = ns.dicts + [ {'entity': entity, 'index': entity | regex_replace('.*_(\d+)', '\\1') | int} ] -%}
    {%- else -%}
      {%- set ns.dicts = ns.dicts + [ {'entity': entity, 'index': -1} ] -%}
    {%- endif -%}
  {%- endfor -%}
  
  [{%- for e in ns.dicts | sort(attribute='index') | map(attribute='entity') | list -%}
    {%- if is_state(e, 'on') -%} {
      'type': 'custom:multiple-entity-row',
      'entity': '{{ e }}',
      'name': '{{ entity_name(e) }}',
      {%- if loop.index0 > 0 -%}
        'attribute': 'hrs_count',
        'secondary_info': {
          'attribute': 'hrs_ranges'
        },
        'entities': []
      {%- endif -%}
    },{%- endif -%}
  {%- endfor -%}]
{%- endmacro -%}
```

Based on the above macro, the below example creates a "MyActivity" card which displays exactly this, assuming an activity "MyActivity" has already been configured.

```yaml
type: custom:auto-entities
card:
  type: entities
  title: MyActivity
  state_color: true
filter:
  template: >-
    {%- from 'weather_activities.jinja' import weather_activities_entities -%}
    {{ weather_activities_entities("binary_sensor.weather_activities_myactivity") }}
```

# Related

* Similar integrations
  * [ha-check-weather](https://github.com/denysdovhan/ha-check-weather) - Excellent, but does not support multi-day per-hour forecasts
  * [ha-car_wash](https://github.com/Limych/ha-car_wash) - Far more restricted functionality

# License

[Apache-2.0](LICENSE)
