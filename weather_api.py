"""
weather_api.py - National Weather Service (NWS) API Module
---------------------------------------------------------
Fetches location via IP Geolocation and queries the US National Weather Service
API for current outdoor weather and forecasts (No API key required).
"""

import requests
import config


class WeatherAPI:
    def __init__(self):
        self.headers = {"User-Agent": config.NWS_USER_AGENT}
        self.timeout = config.NETWORK_TIMEOUT

    def get_ip_location(self):
        """Determines physical location based on public IP address."""
        if not config.AUTO_LOCATION_FROM_IP:
            return {
                "lat": config.DEFAULT_LATITUDE,
                "lon": config.DEFAULT_LONGITUDE,
                "city": config.DEFAULT_CITY_NAME,
                "status": True
            }

        try:
            response = requests.get("http://ip-api.com/json/", timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    return {
                        "lat": round(data.get("lat"), 4),
                        "lon": round(data.get("lon"), 4),
                        "city": data.get("city"),
                        "status": True
                    }
        except Exception as error:
            print(f"IP Location Error: {error}")

        return {
            "lat": config.DEFAULT_LATITUDE,
            "lon": config.DEFAULT_LONGITUDE,
            "city": config.DEFAULT_CITY_NAME,
            "status": False
        }

    def fetch_weather(self, lat=None, lon=None):
        """
        Fetches current weather from NWS using a 2-step lookup:
        Step 1: Get grid station URL via /points/{lat},{lon}
        Step 2: Query grid forecast/observation endpoint
        """
        if lat is None or lon is None:
            location = self.get_ip_location()
            lat = location["lat"]
            lon = location["lon"]
            city_fallback = location["city"]
        else:
            city_fallback = config.DEFAULT_CITY_NAME

        try:
            # Step 1: Query Points Endpoint to get station grid URLs
            points_url = f"https://api.weather.gov/points/{lat},{lon}"
            pts_response = requests.get(points_url, headers=self.headers, timeout=self.timeout)

            if pts_response.status_code != 200:
                print(f"NWS Points Endpoint HTTP Error {pts_response.status_code}")
                return self._fallback_data(city_fallback)

            pts_data = pts_response.json()
            forecast_url = pts_data["properties"]["forecast"]
            
            # Extract city/state from NWS location properties if available
            relative_location = pts_data["properties"]["relativeLocation"]["properties"]
            city_name = relative_location.get("city", city_fallback)

            # Step 2: Fetch Active Forecast
            fc_response = requests.get(forecast_url, headers=self.headers, timeout=self.timeout)
            if fc_response.status_code != 200:
                print(f"NWS Forecast Endpoint HTTP Error {fc_response.status_code}")
                return self._fallback_data(city_name)

            fc_data = fc_response.json()
            current_period = fc_data["properties"]["periods"][0]

            temp = current_period["temperature"]
            
            # Convert units if needed (NWS defaults to Fahrenheit)
            if config.UNITS.lower() == "metric" and current_period["temperatureUnit"] == "F":
                temp = round((temp - 32) * 5 / 9, 1)

            description = current_period["shortForecast"]
            icon_url = current_period.get("icon", "")

            # Infer icon code category from description for renderer
            icon_code = self._get_icon_code(description)

            return {
                "temperature": temp,
                "humidity": current_period.get("relativeHumidity", {}).get("value", "N/A"),
                "description": description,
                "icon_code": icon_code,
                "city": city_name,
                "status": True
            }

        except Exception as error:
            print(f"Failed to fetch NWS weather data: {error}")

        return self._fallback_data(city_fallback)

    def _get_icon_code(self, forecast_str):
        """Maps NWS short forecast text to simple e-Paper icon categories."""
        desc = forecast_str.lower()
        if "rain" in desc or "shower" in desc:
            return "10d"
        elif "cloud" in desc or "overcast" in desc:
            return "03d"
        elif "snow" in desc or "sleet" in desc:
            return "13d"
        elif "thunder" in desc:
            return "11d"
        return "01d"  # Default Sunny / Clear

    def _fallback_data(self, city):
        return {
            "temperature": 0.0,
            "humidity": 0,
            "description": "Offline",
            "icon_code": "01d",
            "city": city,
            "status": False
        }


# ==========================================
# STANDALONE TEST RUNNER
# ==========================================
if __name__ == "__main__":
    print("Testing NWS Weather API...")
    weather = WeatherAPI()
    data = weather.fetch_weather()
    
    if data["status"]:
        print("\n--- NWS Fetch Success ---")
        print(f"Location    : {data['city']}")
        print(f"Temperature : {data['temperature']}°")
        print(f"Humidity    : {data['humidity']}%")
        print(f"Conditions  : {data['description']}")
    else:
        print("\nFailed to fetch weather data. Ensure location is within the United States.")