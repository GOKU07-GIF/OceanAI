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
    max_wind_ms = None
    max_gust_ms = None
    max_rain_probability = None

    for day in evidence.get("forecast_days", []):
        hours = day.get("hours", [])

        day_wind_ms = _max_from_hours(
            hours,
            "wind_speed_m_s",
        )
        day_gust_ms = _max_from_hours(
            hours,
            "gust_speed_m_s",
        )
        day_rain = _max_from_hours(
            hours,
            "rain_probability",
        )

        if day_wind_ms is not None:
            max_wind_ms = (
                day_wind_ms
                if max_wind_ms is None
                else max(max_wind_ms, day_wind_ms)
            )

        if day_gust_ms is not None:
            max_gust_ms = (
                day_gust_ms
                if max_gust_ms is None
                else max(max_gust_ms, day_gust_ms)
            )

        if day_rain is not None:
            max_rain_probability = (
                day_rain
                if max_rain_probability is None
                else max(max_rain_probability, day_rain)
            )

    return {
        "max_wind_ms": max_wind_ms,
        "max_gust_ms": max_gust_ms,
        "max_rain_probability": max_rain_probability,
        "alert_count": len(evidence.get("alerts", [])),
    }


def _extract_ocean(
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    numeric_values: dict[str, list[float]] = {
        "oxygen": [],
        "ph": [],
        "temperature": [],
        "salinity": [],
        "chlorophyll": [],
    }

    for observation in observations:
        for source_key, target_key in (
            ("oxygen", "oxygen"),
            ("ph", "ph"),
            ("temperature_c", "temperature"),
            ("salinity_psu", "salinity"),
            ("chlorophyll_mg_m3", "chlorophyll"),
        ):
            value = observation.get(source_key)
            if isinstance(value, (int, float)):
                numeric_values[target_key].append(float(value))

    return {
        "min_oxygen": (
            min(numeric_values["oxygen"])
            if numeric_values["oxygen"]
            else None
        ),
        "min_ph": (
            min(numeric_values["ph"])
            if numeric_values["ph"]
            else None
        ),
        "max_ph": (
            max(numeric_values["ph"])
            if numeric_values["ph"]
            else None
        ),
        "temperature_min": (
            min(numeric_values["temperature"])
            if numeric_values["temperature"]
            else None
        ),
        "temperature_max": (
            max(numeric_values["temperature"])
            if numeric_values["temperature"]
            else None
        ),
        "salinity_min": (
            min(numeric_values["salinity"])
            if numeric_values["salinity"]
            else None
        ),
        "salinity_max": (
            max(numeric_values["salinity"])
            if numeric_values["salinity"]
            else None
        ),
        "chlorophyll_max": (
            max(numeric_values["chlorophyll"])
            if numeric_values["chlorophyll"]
            else None
        ),
    }


def _extract_marine_conditions(
    agent_results: list[dict[str, Any]],
) -> dict[str, Any]:
    latest: dict[str, Any] = {}

    for result in agent_results:
        if (
            result.get("agent") != "ocean"
            or result.get("status") != "success"
        ):
            continue

        conditions = result.get("conditions")
        if not isinstance(conditions, dict):
            continue

        for key in (
            "wave_height_m",
            "wave_period_s",
            "sst_c",
            "temperature_c",
            "salinity_psu",
            "chlorophyll_mg_m3",
        ):
            if conditions.get(key) is not None:
                latest[key] = conditions[key]

    return latest


def _extract_marine_forecast(
    agent_results: list[dict[str, Any]],
) -> dict[str, Any]:
    values: dict[str, list[float]] = {
        "wave_height_m": [],
        "wave_period_s": [],
        "sst_c": [],
        "salinity_psu": [],
    }

    for result in agent_results:
        if (
            result.get("agent") != "ocean"
            or result.get("status") != "success"
        ):
            continue

        conditions = result.get("conditions")
        if not isinstance(conditions, dict):
            continue

        for key in values:
            value = conditions.get(key)
            if isinstance(value, (int, float)):
                values[key].append(float(value))

    return {
        "max_wave_height_m": (
            max(values["wave_height_m"])
            if values["wave_height_m"]
            else None
        ),
        "min_wave_period_s": (
            min(values["wave_period_s"])
            if values["wave_period_s"]
            else None
        ),
        "latest_sst_c": (
            values["sst_c"][-1]
            if values["sst_c"]
            else None
        ),
        "latest_salinity_psu": (
            values["salinity_psu"][-1]
            if values["salinity_psu"]
            else None
        ),
    }


def run_risk_agent(state: ORCAState) -> dict[str, Any]:
    """Assess risk with deterministic prototype rules.

    Safety blockers are limited to evidence needed for a basic environmental
    go/no-go assessment. Legal restrictions, vessel-specific limits, PFZ
    availability, and biological indicators remain useful limitations/context
    but do not automatically force INSUFFICIENT_EVIDENCE.
    """
    agent_results = state.get("agent_results", [])

    weather_evidence: dict[str, Any] | None = None
    ocean_observations: list[dict[str, Any]] = []

    for result in agent_results:
        if (
            result.get("agent") == "weather"
            and result.get("status") == "success"
        ):
            evidence = result.get("evidence")
            if isinstance(evidence, dict):
                weather_evidence = evidence

        elif (
            result.get("agent") == "ocean"
            and result.get("status") == "success"
        ):
            observations = result.get("observations", [])
            if isinstance(observations, list):
                ocean_observations.extend(
                    item
                    for item in observations
                    if isinstance(item, dict)
                )

    score = 0
    factors: list[str] = []
    limitations: list[str] = []
    decision_blockers: list[str] = []
    dimensions_available = 0

    # --------------------------------------------------------
    # Weather
    # --------------------------------------------------------

    if weather_evidence:
        dimensions_available += 1
        weather = _extract_weather(weather_evidence)

        if weather["alert_count"]:
            score += 3
            factors.append(
                "Active weather alert(s) were reported by WeatherAPI."
            )

        if weather["max_wind_ms"] is not None:
            wind_ms = weather["max_wind_ms"]

            if wind_ms >= 12.5:
                score += 3
                factors.append(
                    "Selected-window forecast wind reaches at least 12.5 m/s."
                )
            elif wind_ms >= 8.3:
                score += 2
                factors.append(
                    "Selected-window forecast wind reaches at least 8.3 m/s."
                )
            elif wind_ms >= 5.6:
                score += 1
                factors.append(
                    "Selected-window forecast wind reaches at least 5.6 m/s."
                )

        if (
            weather["max_gust_ms"] is not None
            and weather["max_gust_ms"] >= 16.7
        ):
            score += 2
            factors.append(
                "Selected-window forecast gusts reach at least 16.7 m/s."
            )

        if (
            weather["max_rain_probability"] is not None
            and weather["max_rain_probability"] >= 70
        ):
            score += 1
            factors.append(
                "Selected-window forecast rain probability reaches at least 70%."
            )
    else:
        decision_blockers.append(
            "Weather forecast evidence is unavailable."
        )
        limitations.append(
            "Weather forecast evidence is unavailable."
        )

    # --------------------------------------------------------
    # Local historical/context observations
    # --------------------------------------------------------

    if ocean_observations:
        dimensions_available += 1
        ocean = _extract_ocean(ocean_observations)

        if (
            ocean["min_oxygen"] is not None
            and ocean["min_oxygen"] < 5
        ):
            factors.append(
                "Nearby OceanAI observations include dissolved oxygen below 5 mg/L."
            )

        if (
            ocean["min_ph"] is not None
            and ocean["min_ph"] < 7
        ):
            factors.append(
                "Nearby OceanAI observations include pH below 7."
            )

        if (
            ocean["max_ph"] is not None
            and ocean["max_ph"] > 9
        ):
            factors.append(
                "Nearby OceanAI observations include pH above 9."
            )

    else:
        limitations.append(
            "No nearby OceanAI observation was available for historical water-quality context."
        )

    # --------------------------------------------------------
    # Copernicus marine conditions
    # --------------------------------------------------------

    marine_forecast = _extract_marine_forecast(
        agent_results
    )

    if marine_forecast["max_wave_height_m"] is not None:
        dimensions_available += 1
        wave_height = marine_forecast["max_wave_height_m"]

        if wave_height >= 3.0:
            score += 4
            factors.append(
                "Marine forecast wave height reaches at least 3.0 m."
            )
        elif wave_height >= 2.0:
            score += 2
            factors.append(
                "Marine forecast wave height reaches at least 2.0 m."
            )
        elif wave_height >= 1.5:
            score += 1
            factors.append(
                "Marine forecast wave height reaches at least 1.5 m."
            )
    else:
        decision_blockers.append(
            "Verified wave-height forecast evidence is unavailable."
        )
        limitations.append(
            "Verified wave-height forecast evidence is unavailable."
        )

    if marine_forecast["min_wave_period_s"] is not None:
        dimensions_available += 1
    else:
        limitations.append(
            "Wave period is not available for sea-state context."
        )

    # These are informative context, not safety score inputs.
    if marine_forecast["latest_sst_c"] is not None:
        factors.append(
            f"Near-surface model temperature is {marine_forecast['latest_sst_c']:.2f} °C."
        )

    if marine_forecast["latest_salinity_psu"] is not None:
        factors.append(
            f"Near-surface model salinity is {marine_forecast['latest_salinity_psu']:.2f} PSU."
        )

    # --------------------------------------------------------
    # Non-blocking limitations
    # --------------------------------------------------------

    limitations.extend(
        [
            "Maritime restriction/geofence data is not yet part of this prototype risk calculation.",
            "Vessel-specific operating limits are not yet part of this prototype risk calculation.",
        ]
    )

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
        "decision_blockers": decision_blockers,
        "marine_context": marine_forecast,
        "method": (
            "Deterministic prototype rules over selected evidence; "
            "missing safety dimensions block a go/no-go decision, while "
            "non-safety context remains visible as a limitation."
        ),
    }

    return {"risk_assessment": assessment}
