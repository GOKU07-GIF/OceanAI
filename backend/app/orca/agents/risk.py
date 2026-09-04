from __future__ import annotations

from typing import Any

from app.orca.state import ORCAState


def _max_from_hours(hours: list[dict[str, Any]], key: str) -> float | None:
    values: list[float] = []
    for hour in hours:
        value = hour.get(key)
        if isinstance(value, (int, float)):
            values.append(float(value))
    return max(values) if values else None


def _extract_weather(evidence: dict[str, Any]) -> dict[str, Any]:
    max_wind = None
    max_gust = None
    max_rain_probability = None

    for day in evidence.get("forecast_days", []):
        hours = day.get("hours", [])
        day_wind = _max_from_hours(hours, "wind_kph")
        day_gust = _max_from_hours(hours, "gust_kph")
        day_rain = _max_from_hours(hours, "rain_probability")

        if day_wind is not None:
            max_wind = day_wind if max_wind is None else max(max_wind, day_wind)
        if day_gust is not None:
            max_gust = day_gust if max_gust is None else max(max_gust, day_gust)
        if day_rain is not None:
            max_rain_probability = (
                day_rain
                if max_rain_probability is None
                else max(max_rain_probability, day_rain)
            )

    return {
        "max_wind_kph": max_wind,
        "max_gust_kph": max_gust,
        "max_rain_probability": max_rain_probability,
        "alert_count": len(evidence.get("alerts", [])),
    }


def _extract_ocean(observations: list[dict[str, Any]]) -> dict[str, Any]:
    numeric_values: dict[str, list[float]] = {
        "oxygen": [],
        "ph": [],
        "temperature": [],
    }

    for observation in observations:
        for source_key, target_key in (
            ("oxygen", "oxygen"),
            ("ph", "ph"),
            ("temperature_c", "temperature"),
        ):
            value = observation.get(source_key)
            if isinstance(value, (int, float)):
                numeric_values[target_key].append(float(value))

    return {
        "min_oxygen": min(numeric_values["oxygen"]) if numeric_values["oxygen"] else None,
        "min_ph": min(numeric_values["ph"]) if numeric_values["ph"] else None,
        "max_ph": max(numeric_values["ph"]) if numeric_values["ph"] else None,
        "temperature_min": min(numeric_values["temperature"]) if numeric_values["temperature"] else None,
        "temperature_max": max(numeric_values["temperature"]) if numeric_values["temperature"] else None,
    }


def _extract_marine_forecast(agent_results: list[dict[str, Any]]) -> dict[str, Any]:
    values: dict[str, list[float]] = {
        "wave_height_m": [],
        "wave_period_s": [],
    }

    for result in agent_results:
        if result.get("agent") != "ocean" or result.get("status") != "success":
            continue
        conditions = result.get("conditions")
        if not isinstance(conditions, dict):
            continue
        for key in values:
            value = conditions.get(key)
            if isinstance(value, (int, float)):
                values[key].append(float(value))

    return {
        "max_wave_height_m": max(values["wave_height_m"]) if values["wave_height_m"] else None,
        "min_wave_period_s": min(values["wave_period_s"]) if values["wave_period_s"] else None,
    }


def run_risk_agent(state: ORCAState) -> dict[str, Any]:
    """Assess marine risk using explicit prototype rules over the selected window.

    This remains a prototype scoring model, not an operational maritime safety
    standard. Missing or unavailable dimensions are reported rather than
    interpreted as safe.
    """
    agent_results = state.get("agent_results", [])

    weather_evidence: dict[str, Any] | None = None
    ocean_observations: list[dict[str, Any]] = []

    for result in agent_results:
        if result.get("agent") == "weather" and result.get("status") == "success":
            weather_evidence = result.get("evidence")
        elif result.get("agent") == "ocean" and result.get("status") == "success":
            ocean_observations.extend(result.get("observations", []))

    score = 0
    factors: list[str] = []
    limitations: list[str] = []
    dimensions_available = 0

    if weather_evidence:
        dimensions_available += 1
        weather = _extract_weather(weather_evidence)

        if weather["alert_count"]:
            score += 3
            factors.append("Active weather alert(s) reported by the weather source.")

        if weather["max_wind_kph"] is not None:
            if weather["max_wind_kph"] >= 45:
                score += 3
                factors.append("Selected-window forecast wind reaches at least 45 km/h.")
            elif weather["max_wind_kph"] >= 30:
                score += 2
                factors.append("Selected-window forecast wind reaches at least 30 km/h.")
            elif weather["max_wind_kph"] >= 20:
                score += 1
                factors.append("Selected-window forecast wind reaches at least 20 km/h.")

        if weather["max_gust_kph"] is not None and weather["max_gust_kph"] >= 60:
            score += 2
            factors.append("Selected-window forecast gusts reach at least 60 km/h.")

        if weather["max_rain_probability"] is not None and weather["max_rain_probability"] >= 70:
            score += 1
            factors.append("Selected-window forecast rain probability reaches at least 70%.")
    else:
        limitations.append("Weather forecast evidence is unavailable.")

    if ocean_observations:
        dimensions_available += 1
        ocean = _extract_ocean(ocean_observations)

        if ocean["min_oxygen"] is not None and ocean["min_oxygen"] < 5:
            score += 1
            factors.append("Nearby OceanAI observations include dissolved oxygen below 5 mg/L.")

        if ocean["min_ph"] is not None and ocean["min_ph"] < 7:
            score += 1
            factors.append("Nearby OceanAI observations include pH below 7.")

        if ocean["max_ph"] is not None and ocean["max_ph"] > 9:
            score += 1
            factors.append("Nearby OceanAI observations include pH above 9.")
    else:
        limitations.append("No nearby OceanAI observation was available for water-quality context.")

    marine_forecast = _extract_marine_forecast(agent_results)
    if marine_forecast["max_wave_height_m"] is not None:
        dimensions_available += 1
        wave_height = marine_forecast["max_wave_height_m"]
        if wave_height >= 3.0:
            score += 4
            factors.append("Marine forecast wave height reaches at least 3.0 m.")
        elif wave_height >= 2.0:
            score += 2
            factors.append("Marine forecast wave height reaches at least 2.0 m.")
        elif wave_height >= 1.5:
            score += 1
            factors.append("Marine forecast wave height reaches at least 1.5 m.")
    else:
        limitations.append("Verified wave-height forecast evidence is unavailable.")

    if marine_forecast["min_wave_period_s"] is not None:
        dimensions_available += 1
    else:
        limitations.append("Wave period is not available for sea-state context.")

    limitations.extend([
        "Maritime restriction/geofence data is not yet part of this risk calculation.",
        "Vessel-specific limits are not yet part of this risk calculation.",
    ])

    if score >= 9:
        level = "CRITICAL"
    elif score >= 6:
        level = "HIGH"
    elif score >= 3:
        level = "MODERATE"
    else:
        level = "LOW"

    if dimensions_available <= 1:
        confidence = "LOW"
    elif dimensions_available == 2:
        confidence = "MEDIUM"
    else:
        confidence = "MEDIUM-HIGH"

    assessment = {
        "overall_risk": level,
        "score": score,
        "confidence": confidence,
        "requested_window": state.get("requested_time"),
        "factors": factors,
        "limitations": limitations,
        "method": "Deterministic prototype rules over the selected evidence window; missing safety dimensions are reported, not assumed safe.",
    }

    return {"risk_assessment": assessment}
