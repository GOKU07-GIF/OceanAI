from __future__ import annotations

import math
import os
from datetime import datetime, timedelta, timezone
from typing import Any

from app.orca.marine.models import MarineDataRequest


COPERNICUS_CHL_DATASET_ID = "cmems_obs-oc_glo_bgc-plankton_nrt_l3-multi-4km_P1D"
COPERNICUS_CHL_VARIABLE = "CHL"


class CopernicusMarineChlorophyllProvider:
    """Copernicus Marine near-real-time ocean-colour chlorophyll adapter.

    The product is a daily satellite observation product, not a future
    forecast. It is therefore only used as observation/context evidence for
    fishing analysis.

    Authentication follows the same policy as the main Copernicus provider:
    explicit environment credentials are used when present; otherwise the
    copernicusmarine package uses credentials saved by `copernicusmarine login`.
    """

    name = "copernicus_chlorophyll"

    def __init__(
        self,
        *,
        dataset_id: str = COPERNICUS_CHL_DATASET_ID,
    ) -> None:
        self.dataset_id = dataset_id

    @staticmethod
    def _scalar(value: Any) -> float | None:
        if value is None:
            return None

        try:
            if hasattr(value, "size") and value.size != 1:
                return None
            if hasattr(value, "item"):
                value = value.item()
            number = float(value)
        except (TypeError, ValueError):
            return None

        return number if math.isfinite(number) else None

    def fetch(self, request: MarineDataRequest) -> dict[str, Any]:
        requested = request.get("variables", [])

        if (
            requested
            and COPERNICUS_CHL_VARIABLE not in requested
            and "chlorophyll_mg_m3" not in requested
        ):
            return {
                "status": "unavailable",
                "error": (
                    "Copernicus chlorophyll adapter supports "
                    "chlorophyll_mg_m3 only."
                ),
            }

        latitude = request.get("latitude")
        longitude = request.get("longitude")

        if latitude is None or longitude is None:
            return {
                "status": "unavailable",
                "error": "Latitude and longitude are required.",
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
            "variables": [COPERNICUS_CHL_VARIABLE],
            "minimum_longitude": float(longitude),
            "maximum_longitude": float(longitude),
            "minimum_latitude": float(latitude),
            "maximum_latitude": float(latitude),
            "coordinates_selection_method": "nearest",
        }

        username = os.getenv(
            "COPERNICUSMARINE_SERVICE_USERNAME"
        )
        password = os.getenv(
            "COPERNICUSMARINE_SERVICE_PASSWORD"
        )

        if username and password:
            kwargs["username"] = username
            kwargs["password"] = password

        # Prefer the caller's requested window. Otherwise only inspect a
        # recent window rather than requesting an unbounded archive.
        if request.get("start_time"):
            kwargs["start_datetime"] = request["start_time"]
        if request.get("end_time"):
            kwargs["end_datetime"] = request["end_time"]

        if not request.get("start_time") and not request.get("end_time"):
            now = datetime.now(timezone.utc)
            kwargs["start_datetime"] = (
                now - timedelta(days=8)
            ).isoformat()
            # Do not force an end time because the product can lag while
            # the latest daily observation is being published.

        try:
            dataset = copernicusmarine.open_dataset(**kwargs)

            selected = dataset.sel(
                latitude=float(latitude),
                longitude=float(longitude),
                method="nearest",
            )

            if "time" in selected.dims:
                selected = selected.isel(time=-1)

            if COPERNICUS_CHL_VARIABLE not in selected.variables:
                return {
                    "status": "unavailable",
                    "error": (
                        "Copernicus Marine returned no chlorophyll variable."
                    ),
                }

            raw_value = selected[COPERNICUS_CHL_VARIABLE].values
            value = self._scalar(raw_value)

            if value is None:
                return {
                    "status": "unavailable",
                    "error": (
                        "Copernicus Marine returned no valid chlorophyll value."
                    ),
                }

            retrieved_at = datetime.now(
                timezone.utc
            ).isoformat(timespec="seconds")

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
                    else retrieved_at
                ),
                "retrieved_at": retrieved_at,
                "chlorophyll_mg_m3": value,
                "quality": "provider-dataset",
                "metadata": {
                    "dataset_id": self.dataset_id,
                    "variable": COPERNICUS_CHL_VARIABLE,
                    "note": (
                        "Near-real-time daily satellite ocean-colour "
                        "observation; not a future forecast."
                    ),
                },
            }

            return {
                "status": "success",
                "data": data,
            }

        except Exception as exc:  # pragma: no cover - provider/network boundary
            return {
                "status": "unavailable",
                "error": (
                    "Copernicus chlorophyll request failed: "
                    f"{exc}"
                ),
            }


copernicus_chlorophyll_provider = CopernicusMarineChlorophyllProvider()
