from __future__ import annotations

from datetime import date, datetime
from typing import Any

import requests

from app.core.config import settings


BASE_URL = "https://api.weatherapi.com/v1/forecast.json"


def get_weather_forecast(
    *,
    latitude: float,
    longitude: float,
    days: int = 2,
) -> dict[str, Any]:
    """Fetch forecast weather and return normalized evidence for ORCA.

    WeatherAPI supports latitude/longitude queries and forecast requests for
    up to 14 days; ORCA only retrieves the next two calendar days for the
    first vertical slice to keep the request focused.
    """
    if not settings.WEATHER_API_KEY:
        return {
            "status": "error",
            "source": "WeatherAPI",
            "error": "Weather API key is not configured.",
        }

    if not 1 <= days <= 14:
        raise ValueError("days must be between 1 and 14")

    params = {
        "key": settings.WEATHER_API_KEY,
        "q": f"{latitude},{longitude}",
        "days": days,
        "aqi": "no",
        "alerts": "yes",
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        return {
            "status": "error",
            "source": "WeatherAPI",
            "error": f"Weather forecast unavailable: {exc}",
        }

    location = data.get("location", {})
    forecast_days = data.get("forecast", {}).get("forecastday", [])
    alerts = data.get("alerts", {}).get("alert", [])

    normalized_days: list[dict[str, Any]] = []
    for forecast_day in forecast_days:
        day = forecast_day.get("day", {})
        hourly = forecast_day.get("hour", [])
        normalized_hours = [
            {
                "time": hour.get("time"),
                "temperature_c": hour.get("temp_c"),
                "feels_like_c": hour.get("feelslike_c"),
                "wind_kph": hour.get("wind_kph"),
                "wind_direction": hour.get("wind_dir"),
                "gust_kph": hour.get("gust_kph"),
                "rain_probability": hour.get("chance_of_rain"),
                "precipitation_mm": hour.get("precip_mm"),
                "condition": hour.get("condition", {}).get("text"),
            }
            for hour in hourly
        ]
        normalized_days.append(
            {
                "date": forecast_day.get("date"),
                "max_temperature_c": day.get("maxtemp_c"),
                "min_temperature_c": day.get("mintemp_c"),
                "avg_temperature_c": day.get("avgtemp_c"),
                "max_wind_kph": day.get("maxwind_kph"),
                "rain_probability": day.get("daily_chance_of_rain"),
                "condition": day.get("condition", {}).get("text"),
                "hours": normalized_hours,
            }
        )

    retrieved_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    evidence = {
        "source": "WeatherAPI",
        "dataset": "Forecast API",
        "type": "forecast",
        "location": {
            "latitude": location.get("lat", latitude),
            "longitude": location.get("lon", longitude),
            "name": location.get("name"),
            "region": location.get("region"),
            "country": location.get("country"),
        },
        "timezone": location.get("tz_id"),
        "retrieved_at": retrieved_at,
        "forecast_days": normalized_days,
        "alerts": alerts,
    }

    return {
        "status": "success",
        "source": "WeatherAPI",
        "last_updated": location.get("localtime"),
        "evidence": evidence,
    }
