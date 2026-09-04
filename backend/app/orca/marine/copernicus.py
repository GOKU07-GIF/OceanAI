from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from app.orca.marine.models import MarineDataRequest


COPERNICUS_WAVE_DATASET_ID = "cmems_mod_glo_wav_anfc_0.083deg_PT3H-i"

# Canonical ORCA variable -> Copernicus Marine variable.
_COPERNICUS_VARIABLES = {
    "wave_height_m": "VHM0",
    "wave_period_s": "VTM10",
    "current_direction_deg": "VMDR",
}


class CopernicusMarineWaveProvider:
    """Copernicus Marine global wave analysis/forecast adapter.

    The adapter uses the official Copernicus Marine Toolbox Python API and
    samples the nearest grid point for the requested location/time window.
    Credentials come only from environment variables; they are never stored
    in the repository.
    """

    name = "copernicus"

    def __init__(self, *, dataset_id: str = COPERNICUS_WAVE_DATASET_ID) -> None:
        self.dataset_id = dataset_id

    def fetch(self, request: MarineDataRequest) -> dict[str, Any]:
        requested = [
            variable
            for variable in request.get("variables", [])
            if variable in _COPERNICUS_VARIABLES
        ]
        if not requested:
            return {
                "status": "unavailable",
                "error": "Copernicus adapter supports wave_height_m, wave_period_s and current_direction_deg.",
            }

        latitude = request.get("latitude")
        longitude = request.get("longitude")
        if latitude is None or longitude is None:
            return {"status": "unavailable", "error": "Latitude and longitude are required."}

        username = os.getenv("COPERNICUSMARINE_SERVICE_USERNAME")
        password = os.getenv("COPERNICUSMARINE_SERVICE_PASSWORD")
        if not username or not password:
            return {
                "status": "unavailable",
                "error": "Copernicus Marine credentials are not configured.",
            }

        try:
            import copernicusmarine
        except ImportError:
            return {
                "status": "unavailable",
                "error": "copernicusmarine package is not installed.",
            }

        variables = [_COPERNICUS_VARIABLES[item] for item in requested]
        kwargs: dict[str, Any] = {
            "dataset_id": self.dataset_id,
            "username": username,
            "password": password,
            "variables": variables,
            "minimum_longitude": longitude,
            "maximum_longitude": longitude,
            "minimum_latitude": latitude,
            "maximum_latitude": latitude,
        }

        if request.get("start_time"):
            kwargs["start_datetime"] = request["start_time"]
        if request.get("end_time"):
            kwargs["end_datetime"] = request["end_time"]

        try:
            dataset = copernicusmarine.open_dataset(**kwargs)
            selected = dataset.sel(
                latitude=latitude,
                longitude=longitude,
                method="nearest",
            )
            if "time" in selected.dims:
                # Keep the first available time in the requested interval. The
                # caller can request a narrow window when it needs a specific slot.
                selected = selected.isel(time=0)

            data: dict[str, Any] = {
                "source": "Copernicus Marine",
                "dataset": self.dataset_id,
                "type": "forecast",
                "location": {
                    "latitude": float(selected.latitude.values),
                    "longitude": float(selected.longitude.values),
                },
                "timestamp": str(selected["time"].values) if "time" in selected.coords else datetime.now(timezone.utc).isoformat(),
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "quality": "provider-dataset",
                "metadata": {
                    "dataset_id": self.dataset_id,
                    "variables": variables,
                    "note": "Global Ocean Waves Analysis and Forecast; sampled at nearest grid point.",
                },
            }

            for canonical, provider_key in _COPERNICUS_VARIABLES.items():
                if canonical not in requested or provider_key not in selected.variables:
                    continue
                raw_value = selected[provider_key].values
                if getattr(raw_value, "size", 1) != 1:
                    raw_value = raw_value.item(0)
                else:
                    raw_value = raw_value.item() if hasattr(raw_value, "item") else raw_value
                if raw_value is not None:
                    data[canonical] = float(raw_value)

            return {"status": "success", "data": data}
        except Exception as exc:  # pragma: no cover - provider/network boundary
            return {
                "status": "unavailable",
                "error": f"Copernicus Marine request failed: {exc}",
            }


copernicus_provider = CopernicusMarineWaveProvider()
