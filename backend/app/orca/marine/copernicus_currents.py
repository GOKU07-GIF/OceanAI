from __future__ import annotations

import math
import os
from datetime import datetime, timezone
from typing import Any

from app.orca.marine.models import MarineDataRequest


DATASET_ID = "cmems_mod_glo_phy_anfc_merged-uv_PT1H-i"


class CopernicusSurfaceCurrentProvider:
    """Fetch Copernicus SMOC surface currents at the nearest grid point."""

    name = "copernicus_currents"

    @staticmethod
    def _credentials() -> tuple[str | None, str | None]:
        return (
            os.getenv("COPERNICUSMARINE_SERVICE_USERNAME"),
            os.getenv("COPERNICUSMARINE_SERVICE_PASSWORD"),
        )

    @staticmethod
    def _scalar(value: Any) -> float | None:
        if value is None:
            return None
        if hasattr(value, "size") and value.size != 1:
            value = value.reshape(-1)[0]
        if hasattr(value, "item"):
            value = value.item()
        return float(value) if isinstance(value, (int, float)) else None

    @staticmethod
    def _speed_direction(u: float, v: float) -> tuple[float, float]:
        speed = math.hypot(u, v)
        direction = (math.degrees(math.atan2(u, v)) + 360.0) % 360.0
        return speed, direction

    def fetch(self, request: MarineDataRequest) -> dict[str, Any]:
        requested = set(request.get("variables", []))
        if not requested.intersection({"current_speed_ms", "current_direction_deg"}):
            return {"status": "unavailable", "error": "No Copernicus current variable requested."}

        latitude = request.get("latitude")
        longitude = request.get("longitude")
        if latitude is None or longitude is None:
            return {"status": "unavailable", "error": "Latitude and longitude are required."}

        username, password = self._credentials()
        if not username or not password:
            return {"status": "unavailable", "error": "Copernicus Marine credentials are not configured."}

        try:
            import copernicusmarine
        except ImportError:
            return {"status": "unavailable", "error": "copernicusmarine package is not installed."}

        try:
            dataset = copernicusmarine.open_dataset(
                dataset_id=DATASET_ID,
                username=username,
                password=password,
                variables=["utotal", "vtotal"],
                minimum_longitude=longitude,
                maximum_longitude=longitude,
                minimum_latitude=latitude,
                maximum_latitude=latitude,
                coordinates_selection_method="nearest",
                start_datetime=request.get("start_time"),
                end_datetime=request.get("end_time"),
            )

            selected = dataset.sel(
                latitude=latitude,
                longitude=longitude,
                method="nearest",
            )
            if "time" in selected.dims:
                selected = selected.isel(time=0)

            u = self._scalar(selected["utotal"].values)
            v = self._scalar(selected["vtotal"].values)
            if u is None or v is None:
                return {"status": "unavailable", "error": "Copernicus returned no surface-current components."}

            speed, direction = self._speed_direction(u, v)
            timestamp = (
                str(selected["time"].values)
                if "time" in selected.coords
                else datetime.now(timezone.utc).isoformat()
            )
            data = {
                "source": "Copernicus Marine",
                "dataset": DATASET_ID,
                "type": "forecast",
                "location": {
                    "latitude": float(selected.latitude.values),
                    "longitude": float(selected.longitude.values),
                },
                "timestamp": timestamp,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "current_speed_ms": speed,
                "current_direction_deg": direction,
                "quality": "provider-dataset",
                "metadata": {
                    "variables": ["utotal", "vtotal"],
                    "note": "SMOC total surface current; derived speed/direction from eastward and northward components.",
                },
            }
            return {"status": "success", "data": data}
        except Exception as exc:  # pragma: no cover - provider/network boundary
            return {"status": "unavailable", "error": f"Copernicus surface-current request failed: {exc}"}


copernicus_currents_provider = CopernicusSurfaceCurrentProvider()
