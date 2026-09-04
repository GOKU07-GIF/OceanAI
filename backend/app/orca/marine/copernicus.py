from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from app.orca.marine.models import MarineDataRequest


COPERNICUS_WAVE_DATASET_ID = "cmems_mod_glo_wav_anfc_0.083deg_PT3H-i"
COPERNICUS_CHL_DATASET_ID = "cmems_obs-oc_glo_bgc-plankton_nrt_l3-multi-4km_P1D"

_WAVE_VARIABLES = {
    "wave_height_m": "VHM0",
    "wave_period_s": "VTM10",
}

_CHL_VARIABLES = {
    "chlorophyll_mg_m3": "CHL",
}


class CopernicusMarineProvider:
    """Copernicus Marine adapters for ORCA ocean conditions.

    One provider name may satisfy multiple canonical fields from different
    Copernicus datasets. Each returned field carries dataset provenance so the
    composite layer never hides where a value came from.
    """

    name = "copernicus"

    def __init__(
        self,
        *,
        wave_dataset_id: str = COPERNICUS_WAVE_DATASET_ID,
        chlorophyll_dataset_id: str = COPERNICUS_CHL_DATASET_ID,
    ) -> None:
        self.wave_dataset_id = wave_dataset_id
        self.chlorophyll_dataset_id = chlorophyll_dataset_id

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

    def _open_dataset(
        self,
        *,
        copernicusmarine: Any,
        dataset_id: str,
        variables: list[str],
        request: MarineDataRequest,
        future_as_latest_observation: bool = False,
    ) -> Any:
        latitude = request["latitude"]
        longitude = request["longitude"]

        kwargs: dict[str, Any] = {
            "dataset_id": dataset_id,
            "username": self._credentials()[0],
            "password": self._credentials()[1],
            "variables": variables,
            "minimum_longitude": longitude,
            "maximum_longitude": longitude,
            "minimum_latitude": latitude,
            "maximum_latitude": latitude,
            "coordinates_selection_method": "nearest",
        }

        start_time = request.get("start_time")
        end_time = request.get("end_time")

        if future_as_latest_observation:
            # Chlorophyll is an observation product, not a forecast. When the
            # user asks about a future window, query the recent NRT archive
            # instead of pretending a future chlorophyll forecast exists.
            now = datetime.now(timezone.utc)
            kwargs["start_datetime"] = (now - timedelta(days=8)).isoformat()
            kwargs["end_datetime"] = now.isoformat()
        else:
            if start_time:
                kwargs["start_datetime"] = start_time
            if end_time:
                kwargs["end_datetime"] = end_time

        return copernicusmarine.open_dataset(**kwargs)

    def _fetch_wave_data(
        self,
        *,
        copernicusmarine: Any,
        request: MarineDataRequest,
        requested: list[str],
    ) -> dict[str, Any] | None:
        dataset = self._open_dataset(
            copernicusmarine=copernicusmarine,
            dataset_id=self.wave_dataset_id,
            variables=[_WAVE_VARIABLES[item] for item in requested],
            request=request,
        )

        selected = dataset.sel(
            latitude=request["latitude"],
            longitude=request["longitude"],
            method="nearest",
        )
        if "time" in selected.dims:
            # For the first vertical slice, one nearest forecast slot is enough.
            selected = selected.isel(time=0)

        data: dict[str, Any] = {
            "source": "Copernicus Marine",
            "dataset": self.wave_dataset_id,
            "type": "forecast",
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
            "quality": "provider-dataset",
            "metadata": {
                "dataset_id": self.wave_dataset_id,
                "variables": [_WAVE_VARIABLES[item] for item in requested],
                "note": "Global Ocean Waves Analysis and Forecast; sampled at nearest grid point.",
            },
        }

        for canonical, provider_key in _WAVE_VARIABLES.items():
            if canonical not in requested or provider_key not in selected.variables:
                continue
            value = self._scalar(selected[provider_key].values)
            if value is not None:
                data[canonical] = value

        return data

    def _fetch_chlorophyll_data(
        self,
        *,
        copernicusmarine: Any,
        request: MarineDataRequest,
    ) -> dict[str, Any] | None:
        dataset = self._open_dataset(
            copernicusmarine=copernicusmarine,
            dataset_id=self.chlorophyll_dataset_id,
            variables=[_CHL_VARIABLES["chlorophyll_mg_m3"]],
            request=request,
            future_as_latest_observation=True,
        )

        selected = dataset.sel(
            latitude=request["latitude"],
            longitude=request["longitude"],
            method="nearest",
        )
        if "time" in selected.dims:
            # Use the latest available observation in the recent NRT archive.
            selected = selected.isel(time=-1)

        value = self._scalar(selected["CHL"].values) if "CHL" in selected.variables else None
        if value is None:
            return None

        return {
            "source": "Copernicus Marine",
            "dataset": self.chlorophyll_dataset_id,
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
            "quality": "provider-dataset",
            "chlorophyll_mg_m3": value,
            "metadata": {
                "dataset_id": self.chlorophyll_dataset_id,
                "variable": "CHL",
                "note": "Latest available Copernicus-GlobColour daily ocean-colour observation in the recent NRT archive; not a forecast.",
            },
        }

    def fetch(self, request: MarineDataRequest) -> dict[str, Any]:
        requested = [
            variable
            for variable in request.get("variables", [])
            if variable in _WAVE_VARIABLES or variable in _CHL_VARIABLES
        ]
        if not requested:
            return {
                "status": "unavailable",
                "error": "Copernicus adapter does not support the requested marine variables.",
            }

        latitude = request.get("latitude")
        longitude = request.get("longitude")
        if latitude is None or longitude is None:
            return {"status": "unavailable", "error": "Latitude and longitude are required."}

        username, password = self._credentials()
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

        data_parts: list[dict[str, Any]] = []
        errors: list[str] = []

        wave_requested = [item for item in requested if item in _WAVE_VARIABLES]
        if wave_requested:
            try:
                wave_data = self._fetch_wave_data(
                    copernicusmarine=copernicusmarine,
                    request=request,
                    requested=wave_requested,
                )
                if wave_data:
                    data_parts.append(wave_data)
            except Exception as exc:  # pragma: no cover - provider/network boundary
                errors.append(f"wave dataset: {exc}")

        if "chlorophyll_mg_m3" in requested:
            try:
                chlorophyll_data = self._fetch_chlorophyll_data(
                    copernicusmarine=copernicusmarine,
                    request=request,
                )
                if chlorophyll_data:
                    data_parts.append(chlorophyll_data)
            except Exception as exc:  # pragma: no cover - provider/network boundary
                errors.append(f"chlorophyll dataset: {exc}")

        if not data_parts:
            return {
                "status": "unavailable",
                "error": "No requested Copernicus marine variable could be retrieved.",
                "details": errors,
            }

        return {
            "status": "success",
            "data_parts": data_parts,
            "errors": errors,
        }


copernicus_provider = CopernicusMarineProvider()
