from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import requests

from app.core.config import settings


BASE_URL = "https://api.weatherapi.com/v1/forecast.json"


def _parse_window(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _wind_ms(wind_kph: Any) -> float | None:
    """Convert WeatherAPI km/h to canonical m/s."""
    if not isinstance(wind_kph, (int, float)):
        return None
    return round(float(wind_kph) / 3.6, 3)


def _filter_forecast_days(
    forecast_days: list[dict[str, Any]],
    *,
    start_time: str | None,
    end_time: str | None,
) -> list[dict[str, Any]]:
    """Keep only hourly forecast values inside the requested local window."""
    start = _parse_window(start_time)
    end = _parse_window(end_time)
    if start is None or end is None:
        return forecast_days

    if start.tzinfo is not None:
        start = start.replace(tzinfo=None)
    if end.tzinfo is not None:
        end = end.replace(tzinfo=None)

    filtered_days: list[dict[str, Any]] = []

    for day in forecast_days:
        filtered_hours: list[dict[str, Any]] = []

        for hour in day.get("hours", []):
            raw = hour.get("time")

            try:
                hour_dt = datetime.fromisoformat(str(raw))
            except (TypeError, ValueError):
                continue

            if start <= hour_dt <= end:
                filtered_hours.append(hour)

        if filtered_hours:
            filtered_day = dict(day)
            filtered_day["hours"] = filtered_hours
            filtered_day["selected_hour_count"] = len(filtered_hours)
            filtered_days.append(filtered_day)

    return filtered_days


def get_weather_forecast(
    *,
    latitude: float,
    longitude: float,
    days: int = 2,
    start_time: str | None = None,
    end_time: str | None = None,
) -> dict[str, Any]:
    """Fetch WeatherAPI forecast and return normalized ORCA evidence."""
    if not settings.WEATHER_API_KEY:
        return {
            "status": "error",
            "source": "WeatherAPI",
            "error": "Weather API key is not configured.",
        }

    start = _parse_window(start_time)
    end = _parse_window(end_time)

    if start and end and end < start:
        return {
            "status": "error",
            "source": "WeatherAPI",
            "error": "Requested weather time window is invalid: end precedes start.",
        }

    if start and end:
        current_local_date = (
            datetime.now(start.tzinfo).date()
            if start.tzinfo
            else datetime.now().date()
        )
        days = max(
            1,
            (end.date() - current_local_date).days + 1,
        )
        days = max(days, 2)

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
        response = requests.get(
            BASE_URL,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        return {
            "status": "error",
            "source": "WeatherAPI",
            "error": f"Weather forecast unavailable: {exc}",
        }

    location = data.get("location", {})
    raw_forecast_days = data.get(
        "forecast",
        {},
    ).get("forecastday", [])
    alerts = data.get("alerts", {}).get(
        "alert",
        [],
    )

    normalized_days: list[dict[str, Any]] = []

    for forecast_day in raw_forecast_days:
        day = forecast_day.get("day", {})
        hourly = forecast_day.get("hour", [])

        normalized_hours: list[dict[str, Any]] = []

        for hour in hourly:
            wind_kph = hour.get("wind_kph")
            gust_kph = hour.get("gust_kph")

            normalized_hours.append(
                {
                    "time": hour.get("time"),
                    "temperature_c": hour.get("temp_c"),
                    "feels_like_c": hour.get("feelslike_c"),
                    "wind_kph": wind_kph,
                    "wind_speed_m_s": _wind_ms(wind_kph),
                    "wind_direction": hour.get("wind_dir"),
                    "gust_kph": gust_kph,
                    "gust_speed_m_s": _wind_ms(gust_kph),
                    "rain_probability": hour.get("chance_of_rain"),
                    "precipitation_mm": hour.get("precip_mm"),
                    "condition": hour.get("condition", {}).get("text"),
                }
            )

        max_wind_kph = day.get("maxwind_kph")

        normalized_days.append(
            {
                "date": forecast_day.get("date"),
                "max_temperature_c": day.get("maxtemp_c"),
                "min_temperature_c": day.get("mintemp_c"),
                "avg_temperature_c": day.get("avgtemp_c"),
                "max_wind_kph": max_wind_kph,
                "max_wind_speed_m_s": _wind_ms(max_wind_kph),
                "rain_probability": day.get("daily_chance_of_rain"),
                "condition": day.get("condition", {}).get("text"),
                "hours": normalized_hours,
            }
        )

    selected_days = _filter_forecast_days(
        normalized_days,
        start_time=start_time,
        end_time=end_time,
    )

    # A compact canonical wind value is useful to the ORCA frontend while
    # keeping the complete hourly evidence for the risk engine.
    latest_hour: dict[str, Any] | None = None
    for day in reversed(selected_days):
        if day.get("hours"):
            latest_hour = day["hours"][-1]
            break

    if latest_hour is None:
        for day in reversed(normalized_days):
            if day.get("hours"):
                latest_hour = day["hours"][-1]
                break

    retrieved_at = datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")

    evidence: dict[str, Any] = {
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
        "requested_window": {
            "start": start_time,
            "end": end_time,
        },
        "forecast_days": selected_days,
        "alerts": alerts,
    }

    if latest_hour:
        evidence["wind_speed_m_s"] = latest_hour.get(
            "wind_speed_m_s"
        )
        evidence["wind_kph"] = latest_hour.get(
            "wind_kph"
        )
        evidence["wind_direction"] = latest_hour.get(
            "wind_direction"
        )
        evidence["wind_timestamp"] = latest_hour.get(
            "time"
        )

    if start and end and not selected_days:
        evidence["window_warning"] = (
            "No hourly forecast records matched the requested time window."
        )

    return {
        "status": "success",
        "source": "WeatherAPI",
        "last_updated": location.get("localtime"),
        "evidence": evidence,
    }
