from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from app.orca.marine.models import MarineDataRequest


COPERNICUS_CHL_DATASET_ID = "cmems_obs-oc_glo_bgc-plankton_nrt_l3-multi-4km_P1D"
COPERNICUS_CHL_VARIABLE = "CHL"


class CopernicusMarineChlorophyllProvider:
    """Copernicus Marine near-real-time ocean-colour chlorophyll adapter.

    The product is a daily satellite observation product, not a future
    forecast. It is therefore only used as observation/context evidence for
    fishing analysis.
    """

    name = "copernicus_chlorophyll"

    def __init__(self, *, dataset_id: str = COPERNICUS_CHL_DATASET_ID) -> None:
        self.dataset_id = dataset_id

    def fetch(self, request: MarineDataRequest) -> dict[str, Any]:
        requested = request.get("variables", [])
        if requested and COPERNICUS_CHL_VARIABLE not in requested and "chlorophyll_mg_m3" not in requested:
            return {
                "status": "unavailable",
                "error": "Copernicus chlorophyll adapter supports chlorophyll_mg_m3 only.",
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

        kwargs: dict[str, Any] = {
            "dataset_id": self.dataset_id,
            "username": username,
            "password": password,
            "variables": [COPERNICUS_CHL_VARIABLE],
            "minimum_longitude": longitude,
            "maximum_longitude": longitude,
            "minimum_latitude": latitude,
            "maximum_latitude": latitude,
            "coordinates_selection_method": "nearest",
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
                selected = selected.isel(time=0)

            raw_value = selected[COPERNICUS_CHL_VARIABLE].values
            if hasattr(raw_value, "size") and raw_value.size != 1:
                raw_value = raw_value.reshape(-1)[0]
            if hasattr(raw_value, "item"):
                raw_value = raw_value.item()

            if raw_value is None:
                return {
                    "status": "unavailable",
                    "error": "Copernicus Marine returned no chlorophyll value.",
                }

            data: dict[str, Any] = {
                "source": "Copernicus Marine",
                "dataset": self.dataset_id,
                "type": "observation",
                "location": {
                    "latitude": float(selected.latitude.values),
                    "longitude": float(selected.longitude.values),
                },
                "timestamp": (
                    str(selected["time"].values)
                    if "time" in selected.coords
                    else datetime.now(timezone.utc).isoformat()
                ),
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "chlorophyll_mg_m3": float(raw_value),
                "quality": "provider-dataset",
                "metadata": {
                    "dataset_id": self.dataset_id,
                    "variable": COPERNICUS_CHL_VARIABLE,
                    "note": "Near-real-time daily satellite ocean-colour observation; not a future forecast.",
                },
            }
            return {"status": "success", "data": data}
        except Exception as exc:  # pragma: no cover - provider/network boundary
            return {
                "status": "unavailable",
                "error": f"Copernicus chlorophyll request failed: {exc}",
            }


copernicus_chlorophyll_provider = CopernicusMarineChlorophyllProvider()
