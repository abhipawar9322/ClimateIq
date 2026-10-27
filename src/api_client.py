"""
External Climate API Integration Client for ClimateIQ.
Queries Open-Meteo free public climate endpoints for live meteorological indicators,
with transparent offline fallback to local benchmarks if disconnected.
"""

from typing import Dict, Any, Optional, Tuple
import requests


OPEN_METEO_GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_live_city_weather(
    city_name: str,
    timeout_sec: float = 4.0
) -> Dict[str, Any]:
    """
    Fetches real-time atmospheric measurements for a city via Open-Meteo.
    Falls back gracefully if offline.
    
    Returns:
        Dict with keys: success, is_live, city, latitude, longitude,
        temperature_c, humidity_pct, precipitation_mm, wind_speed_kmh,
        weather_description, error_message
    """
    try:
        # 1. Geocode city
        geo_params = {"name": city_name, "count": 1, "language": "en", "format": "json"}
        geo_resp = requests.get(OPEN_METEO_GEO_URL, params=geo_params, timeout=timeout_sec)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()
        
        results = geo_data.get("results", [])
        if not results:
            return {
                "success": False,
                "is_live": False,
                "error_message": f"City '{city_name}' not found in global geocoding registry."
            }
            
        loc = results[0]
        lat = loc["latitude"]
        lon = loc["longitude"]
        country = loc.get("country", "")
        elevation = loc.get("elevation", 0)
        
        # 2. Query forecast & current atmospheric stress metrics
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
            "timezone": "auto"
        }
        w_resp = requests.get(OPEN_METEO_FORECAST_URL, params=weather_params, timeout=timeout_sec)
        w_resp.raise_for_status()
        w_data = w_resp.json()
        
        curr = w_data.get("current", {})
        temp = curr.get("temperature_2m", 22.0)
        humidity = curr.get("relative_humidity_2m", 50.0)
        precip = curr.get("precipitation", 0.0)
        wind = curr.get("wind_speed_10m", 10.0)
        
        # Compute thermal heat index (approximate Rothfusz formula)
        # Wet-bulb / Heat stress proxy
        heat_index = temp + 0.33 * (humidity / 100.0 * 6.105 * (2.71828 ** ((17.27 * temp) / (237.7 + temp)))) - 4.0
        
        daily = w_data.get("daily", {})
        daily_max_temp = daily.get("temperature_2m_max", [temp])[0]
        daily_precip_sum = daily.get("precipitation_sum", [precip])[0]
        
        return {
            "success": True,
            "is_live": True,
            "city": city_name,
            "country": country,
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "elevation_m": elevation,
            "temperature_c": round(temp, 1),
            "humidity_pct": round(humidity, 1),
            "precipitation_mm": round(precip, 2),
            "wind_speed_kmh": round(wind, 1),
            "heat_index_c": round(heat_index, 1),
            "daily_max_temp_c": round(daily_max_temp, 1),
            "daily_precip_sum_mm": round(daily_precip_sum, 1),
            "error_message": None
        }
        
    except (requests.RequestException, Exception) as exc:
        return {
            "success": False,
            "is_live": False,
            "error_message": f"External API connection notice: {str(exc)}. Reverting to verified offline benchmark models."
        }
