SKILL_DESCRIPTION = "Get current weather for a city by name"
SKILL_PARAMETERS = {"city": "Name of the city"}

import urllib.request
import json

def run(params: dict) -> str:
    city = params.get("city", "")
    
    # First, geocode the city
    geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    with urllib.request.urlopen(geocode_url) as resp:
        geo_data = json.loads(resp.read().decode())
    
    if "results" not in geo_data or len(geo_data["results"]) == 0:
        return f"Could not find city: {city}"
    
    result = geo_data["results"][0]
    lat = result["latitude"]
    lon = result["longitude"]
    city_name = result["name"]
    country = result.get("country", "")
    
    # Get current weather
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m"
        f"&timezone=auto"
    )
    
    with urllib.request.urlopen(weather_url) as resp:
        weather_data = json.loads(resp.read().decode())
    
    current = weather_data["current"]
    temp = current["temperature_2m"]
    feels_like = current["apparent_temperature"]
    humidity = current["relative_humidity_2m"]
    wind = current["wind_speed_10m"]
    weather_code = current["weather_code"]
    
    # WMO weather codes
    wmo_codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
    }
    description = wmo_codes.get(weather_code, f"Code {weather_code}")
    
    return (
        f"Current weather in {city_name}, {country}:\n"
        f"  Condition: {description}\n"
        f"  Temperature: {temp}°C (feels like {feels_like}°C)\n"
        f"  Humidity: {humidity}%\n"
        f"  Wind speed: {wind} km/h"
    )
