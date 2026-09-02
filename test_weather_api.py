import json

import weather_api


class DummyResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_get_weather_data_returns_expected_dictionary(monkeypatch):
    points_payload = {
        "properties": {
            "forecast": "https://api.weather.gov/gridpoints/MPX/100,100/forecast",
            "forecastHourly": "https://api.weather.gov/gridpoints/MPX/100,100/forecast/hourly",
            "observationStations": "https://api.weather.gov/stations/ABC/observations",
        }
    }

    forecast_payload = {
        "properties": {
            "periods": [
                {
                    "name": "Tonight",
                    "temperature": 61,
                    "temperatureUnit": "F",
                    "shortForecast": "Clear",
                    "isDaytime": False,
                },
                {
                    "name": "Monday",
                    "temperature": 78,
                    "temperatureUnit": "F",
                    "shortForecast": "Partly Sunny",
                    "isDaytime": True,
                },
            ]
        }
    }

    observations_payload = {
        "properties": {
            "temperature": {"value": 23.0, "unitCode": "wmoUnit:degC"},
            "textDescription": "Partly Sunny",
        }
    }

    def fake_urlopen(url, timeout=30):
        if "points" in url:
            return DummyResponse(points_payload)
        if "/forecast" in url and "hourly" not in url:
            return DummyResponse(forecast_payload)
        if "observations" in url:
            return DummyResponse(observations_payload)
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr(weather_api, "_load_config", lambda: {"location": {"latitude": 40.2338, "longitude": -111.6585}, "general": {"units": "fahrenheit"}})
    monkeypatch.setattr(weather_api.urllib.request, "urlopen", fake_urlopen)

    result = weather_api.get_weather_data()

    assert result["temperature"] == 73.4
    assert result["conditions"] == "Partly Sunny"
    assert result["high"] == 78.0
    assert result["low"] == 61.0
