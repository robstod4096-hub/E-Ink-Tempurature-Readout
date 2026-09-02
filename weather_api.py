import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import tomllib


def _load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.toml")
    with open(config_path, "rb") as config_file:
        return tomllib.load(config_file)


def _fetch_json(url):
    request = Request(url, headers={"User-Agent": "E-Ink-Temperature-Readout/1.0"})
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _convert_temperature_to_fahrenheit(value, unit_code=None):
    if value is None:
        return None

    if unit_code and "degC" in unit_code:
        return (float(value) * 9 / 5) + 32

    return float(value)


def _convert_temperature_to_target_units(value, target_units):
    if value is None:
        return None

    value = float(value)
    if target_units == "celsius":
        return (value - 32) * 5 / 9

    return value


def get_weather_data():
    config = _load_config()
    latitude = config["location"]["latitude"]
    longitude = config["location"]["longitude"]
    preferred_units = config["general"].get("units", "fahrenheit").lower()

    try:
        points_url = f"https://api.weather.gov/points/{latitude},{longitude}"
        points_data = _fetch_json(points_url)
        points_properties = points_data.get("properties", {})

        forecast_url = points_properties.get("forecast")
        if not forecast_url:
            raise ValueError("Forecast URL not found in points response")

        forecast_data = _fetch_json(forecast_url)
        periods = forecast_data.get("properties", {}).get("periods", [])

        high = None
        low = None
        for period in periods:
            temperature = period.get("temperature")
            if temperature is None:
                continue

            temperature_fahrenheit = _convert_temperature_to_fahrenheit(
                temperature,
                period.get("temperatureUnit"),
            )
            if temperature_fahrenheit is None:
                continue

            if period.get("isDaytime"):
                if high is None or temperature_fahrenheit > high:
                    high = temperature_fahrenheit
            else:
                if low is None or temperature_fahrenheit < low:
                    low = temperature_fahrenheit

        conditions = "Unavailable"
        current_temperature = None

        observation_stations = points_properties.get("observationStations")
        if observation_stations:
            station_collection = _fetch_json(observation_stations)
            features = station_collection.get("features", [])
            if features:
                station_url = features[0].get("id")
                if station_url:
                    latest_observation = _fetch_json(f"{station_url}/observations/latest")
                    properties = latest_observation.get("properties", {})
                    observation = properties.get("temperature")
                    if observation:
                        current_temperature = _convert_temperature_to_fahrenheit(
                            observation.get("value"),
                            observation.get("unitCode"),
                        )
                    conditions = properties.get("textDescription") or conditions

        if current_temperature is None and periods:
            current_period = periods[0]
            current_temperature = _convert_temperature_to_fahrenheit(
                current_period.get("temperature"),
                current_period.get("temperatureUnit"),
            )
            conditions = current_period.get("shortForecast") or conditions

        if preferred_units == "celsius":
            if current_temperature is not None:
                current_temperature = _convert_temperature_to_target_units(current_temperature, "celsius")
            if high is not None:
                high = _convert_temperature_to_target_units(high, "celsius")
            if low is not None:
                low = _convert_temperature_to_target_units(low, "celsius")

        return {
            "temperature": current_temperature,
            "conditions": conditions,
            "high": high,
            "low": low,
            "unit": preferred_units,
        }

    except (HTTPError, URLError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return {
            "temperature": None,
            "conditions": "Unavailable",
            "high": None,
            "low": None,
            "unit": preferred_units,
            "error": str(exc),
        }
