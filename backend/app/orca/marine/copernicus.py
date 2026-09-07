from __future__ import annotations

import math
import os
from datetime import datetime, timedelta, timezone
from typing import Any

import numpy as np

from app.orca.marine.models import MarineDataRequest


COPERNICUS_WAVE_DATASET_ID = "cmems_mod_glo_wav_anfc_0.083deg_PT3H-i"
COPERNICUS_CHL_DATASET_ID = "cmems_obs-oc_glo_bgc-plankton_nrt_l3-multi-4km_P1D"
COPERNICUS_TEMP_DATASET_ID = "cmems_mod_glo_phy-thetao_anfc_0.083deg_PT6H-i"
COPERNICUS_SALINITY_DATASET_ID = "cmems_mod_glo_phy-so_anfc_0.083deg_PT6H-i"


_WAVE_VARIABLES = {
    "wave_height_m": "VHM0",
    "wave_period_s": "VTM02",
}

_CHL_VARIABLES = {"chlorophyll_mg_m3": "CHL"}

_PHYSICS_VARIABLES = {
    "sst_c": (COPERNICUS_TEMP_DATASET_ID, "thetao"),
    "temperature_c": (COPERNICUS_TEMP_DATASET_ID, "thetao"),
    "salinity_psu": (COPERNICUS_SALINITY_DATASET_ID, "so"),
}


class CopernicusMarineProvider:
    """Copernicus Marine adapter used by ORCA."""

    name = "copernicus"

    def __init__(
        self,
        *,
        wave_dataset_id: str = COPERNICUS_WAVE_DATASET_ID,
        chlorophyll_dataset_id: str = COPERNICUS_CHL_DATASET_ID,
        temperature_dataset_id: str = COPERNICUS_TEMP_DATASET_ID,
        salinity_dataset_id: str = COPERNICUS_SALINITY_DATASET_ID,
    ) -> None:
        self.wave_dataset_id = wave_dataset_id
        self.chlorophyll_dataset_id = chlorophyll_dataset_id
        self.temperature_dataset_id = temperature_dataset_id
        self.salinity_dataset_id = salinity_dataset_id

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
        try:
            if hasattr(value, "size") and value.size != 1:
                return None
            if hasattr(value, "item"):
                value = value.item()
            number = float(value)
        except (TypeError, ValueError):
            return None
        return number if math.isfinite(number) else None

    @staticmethod
    def _degrees_for_km(radius_km: float) -> tuple[float, float]:
        radius_km = max(float(radius_km), 0.0)
        return radius_km / 111.0, radius_km / 104.0

    @staticmethod
    def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        rlat1 = math.radians(lat1)
        rlat2 = math.radians(lat2)
        dlat = rlat2 - rlat1
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2.0) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2.0) ** 2
        return 6371.0 * 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(1.0 - a, 0.0)))

    def _open_dataset(
        self,
        *,
        copernicusmarine: Any,
        dataset_id: str,
        variables: list[str],
        request: MarineDataRequest,
        minimum_depth: float | None = None,
        maximum_depth: float | None = None,
        recent_observation_days: int | None = None,
        search_radius_km: float | None = None,
    ) -> Any:
        latitude = float(request["latitude"])
        longitude = float(request["longitude"])
        min_lon = max_lon = longitude
        min_lat = max_lat = latitude

        if search_radius_km is not None and search_radius_km > 0:
            lat_padding, lon_padding = self._degrees_for_km(search_radius_km)
            min_lon = max(-180.0, longitude - lon_padding)
            max_lon = min(180.0, longitude + lon_padding)
            min_lat = max(-90.0, latitude - lat_padding)
            max_lat = min(90.0, latitude + lat_padding)

        kwargs: dict[str, Any] = {
            "dataset_id": dataset_id,
            "variables": variables,
            "minimum_longitude": min_lon,
            "maximum_longitude": max_lon,
            "minimum_latitude": min_lat,
            "maximum_latitude": max_lat,
            "coordinates_selection_method": "inside" if search_radius_km is not None else "nearest",
        }

        username, password = self._credentials()
        if username and password:
            kwargs["username"] = username
            kwargs["password"] = password

        if minimum_depth is not None:
            kwargs["minimum_depth"] = minimum_depth
        if maximum_depth is not None:
            kwargs["maximum_depth"] = maximum_depth

        start_time = request.get("start_time")
        end_time = request.get("end_time")
        if start_time:
            kwargs["start_datetime"] = start_time
        if end_time:
            kwargs["end_datetime"] = end_time

        if recent_observation_days is not None:
            now = datetime.now(timezone.utc)
            kwargs["start_datetime"] = (now - timedelta(days=recent_observation_days)).isoformat()
            kwargs["end_datetime"] = now.isoformat()
        elif not start_time and not end_time:
            now = datetime.now(timezone.utc)
            kwargs["start_datetime"] = (now - timedelta(days=1)).isoformat()
            kwargs["end_datetime"] = now.isoformat()

        return copernicusmarine.open_dataset(**kwargs)

    def _has_valid_wave_value(self, selected: Any, requested: list[str]) -> bool:
        return any(
            _WAVE_VARIABLES[item] in selected.variables
            and self._scalar(selected[_WAVE_VARIABLES[item]].values) is not None
            for item in requested
        )

    def _nearest_valid_wave_point(
        self,
        dataset: Any,
        requested: list[str],
        requested_latitude: float,
        requested_longitude: float,
    ) -> tuple[Any, float, float, float] | None:
        if "latitude" not in dataset.coords or "longitude" not in dataset.coords:
            return None

        latitude_values = np.asarray(dataset["latitude"].values).reshape(-1)
        longitude_values = np.asarray(dataset["longitude"].values).reshape(-1)
        candidates: list[tuple[float, float, float]] = []
        for lat in latitude_values:
            for lon in longitude_values:
                lat_f, lon_f = float(lat), float(lon)
                candidates.append((self._distance_km(requested_latitude, requested_longitude, lat_f, lon_f), lat_f, lon_f))
        candidates.sort(key=lambda item: item[0])

        for distance, lat, lon in candidates:
            try:
                selected = dataset.sel(latitude=lat, longitude=lon, method="nearest")
                if "time" in selected.dims:
                    selected = selected.isel(time=-1)
                if self._has_valid_wave_value(selected, requested):
                    return selected, lat, lon, distance
            except Exception:
                continue
        return None

    def _fetch_wave_data(self, *, copernicusmarine: Any, request: MarineDataRequest, requested: list[str]) -> dict[str, Any] | None:
        requested_latitude = float(request["latitude"])
        requested_longitude = float(request["longitude"])
        dataset = self._open_dataset(
            copernicusmarine=copernicusmarine,
            dataset_id=self.wave_dataset_id,
            variables=[_WAVE_VARIABLES[item] for item in requested],
            request=request,
        )

        selected = dataset.sel(latitude=requested_latitude, longitude=requested_longitude, method="nearest")
        if "time" in selected.dims:
            selected = selected.isel(time=-1)

        snapped = False
        selected_latitude = float(selected.latitude.values)
        selected_longitude = float(selected.longitude.values)
        distance = self._distance_km(requested_latitude, requested_longitude, selected_latitude, selected_longitude)

        if not self._has_valid_wave_value(selected, requested):
            try:
                dataset.close()
            except Exception:
                pass

            try:
                dataset = self._open_dataset(
                    copernicusmarine=copernicusmarine,
                    dataset_id=self.wave_dataset_id,
                    variables=[_WAVE_VARIABLES[item] for item in requested],
                    request=request,
                    search_radius_km=float(request.get("radius_km", 50.0) or 50.0),
                )
                found = self._nearest_valid_wave_point(
                    dataset,
                    requested,
                    requested_latitude,
                    requested_longitude,
                )
            except Exception:
                found = None

            if found is None:
                return None
            selected, selected_latitude, selected_longitude, distance = found
            snapped = True

        timestamp = str(selected["time"].values) if "time" in selected.coords else datetime.now(timezone.utc).isoformat()
        result: dict[str, Any] = {
            "source": "Copernicus Marine",
            "dataset": self.wave_dataset_id,
            "type": "forecast",
            "location": {"latitude": selected_latitude, "longitude": selected_longitude},
            "timestamp": timestamp,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "quality": "provider-dataset",
            "metadata": {
                "dataset_id": self.wave_dataset_id,
                "variables": [_WAVE_VARIABLES[item] for item in requested],
                "requested_location": {"latitude": requested_latitude, "longitude": requested_longitude},
                "location_snap_distance_km": distance,
                "snapped_to_nearest_valid_ocean_cell": snapped,
            },
        }

        for canonical in requested:
            provider_key = _WAVE_VARIABLES[canonical]
            if provider_key in selected.variables:
                value = self._scalar(selected[provider_key].values)
                if value is not None:
                    result[canonical] = value

        return result if self._has_valid_wave_value(selected, requested) else None

    def _fetch_chlorophyll_data(self, *, copernicusmarine: Any, request: MarineDataRequest) -> dict[str, Any] | None:
        dataset = self._open_dataset(
            copernicusmarine=copernicusmarine,
            dataset_id=self.chlorophyll_dataset_id,
            variables=["CHL"],
            request=request,
            recent_observation_days=8,
        )
        selected = dataset.sel(latitude=request["latitude"], longitude=request["longitude"], method="nearest")
        if "time" in selected.dims:
            selected = selected.isel(time=-1)
        if "CHL" not in selected.variables:
            return None
        value = self._scalar(selected["CHL"].values)
        if value is None:
            return None
        return {
            "source": "Copernicus Marine",
            "dataset": self.chlorophyll_dataset_id,
            "type": "observation",
            "location": {"latitude": float(selected.latitude.values), "longitude": float(selected.longitude.values)},
            "timestamp": str(selected["time"].values) if "time" in selected.coords else datetime.now(timezone.utc).isoformat(),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "quality": "provider-dataset",
            "chlorophyll_mg_m3": value,
            "metadata": {"dataset_id": self.chlorophyll_dataset_id, "variable": "CHL"},
        }

    def _fetch_physics_data(self, *, copernicusmarine: Any, request: MarineDataRequest, canonical: str) -> dict[str, Any] | None:
        dataset_id, provider_variable = _PHYSICS_VARIABLES[canonical]
        dataset = self._open_dataset(
            copernicusmarine=copernicusmarine,
            dataset_id=dataset_id,
            variables=[provider_variable],
            request=request,
            minimum_depth=0.5,
            maximum_depth=10.0,
        )
        selected = dataset.sel(latitude=request["latitude"], longitude=request["longitude"], method="nearest")
        if "time" in selected.dims:
            selected = selected.isel(time=-1)

        field = selected[provider_variable]
        has_depth = "depth" in field.dims
        depth_count = field.sizes.get("depth", 1)
        time_count = field.sizes.get("time", 1)

        value: float | None = None
        timestamp: str | None = None
        depth_m: float | None = None
        for time_index in range(time_count - 1, -1, -1):
            for depth_index in range(depth_count):
                indexers: dict[str, int] = {}
                if "time" in field.dims:
                    indexers["time"] = time_index
                if has_depth:
                    indexers["depth"] = depth_index
                candidate = self._scalar(field.isel(**indexers).values)
                if candidate is not None:
                    value = candidate
                    if "time" in selected.coords:
                        try:
                            timestamp = str(selected["time"].isel(time=time_index).values)
                        except Exception:
                            timestamp = None
                    if has_depth and "depth" in selected.coords:
                        depth_m = self._scalar(selected["depth"].isel(depth=depth_index).values)
                    break
            if value is not None:
                break

        if value is None:
            return None

        data: dict[str, Any] = {
            "source": "Copernicus Marine",
            "dataset": dataset_id,
            "type": "forecast",
            "location": {"latitude": float(selected.latitude.values), "longitude": float(selected.longitude.values)},
            "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "depth_m": depth_m,
            "quality": "provider-dataset",
            "metadata": {"dataset_id": dataset_id, "variable": provider_variable, "depth_m": depth_m},
        }
        if canonical in {"sst_c", "temperature_c"}:
            data["sst_c"] = value
            data["temperature_c"] = value
            data["metadata"]["note"] = "Near-surface Copernicus model potential temperature used as a surface-temperature proxy; not satellite SST."
        else:
            data["salinity_psu"] = value
            data["metadata"]["note"] = "Near-surface Copernicus model salinity from the latest valid shallow ocean level."
        return data

    def fetch(self, request: MarineDataRequest) -> dict[str, Any]:
        supported = set(_WAVE_VARIABLES) | set(_CHL_VARIABLES) | set(_PHYSICS_VARIABLES)
        requested = [item for item in request.get("variables", []) if item in supported]
        if not requested:
            return {"status": "unavailable", "error": "Copernicus adapter does not support the requested marine variables."}
        if request.get("latitude") is None or request.get("longitude") is None:
            return {"status": "unavailable", "error": "Latitude and longitude are required."}

        try:
            import copernicusmarine
        except ImportError:
            return {"status": "unavailable", "error": "copernicusmarine package is not installed."}

        data_parts: list[dict[str, Any]] = []
        errors: list[str] = []

        wave_requested = [item for item in requested if item in _WAVE_VARIABLES]
        if wave_requested:
            try:
                value = self._fetch_wave_data(copernicusmarine=copernicusmarine, request=request, requested=wave_requested)
                if value:
                    data_parts.append(value)
            except Exception as exc:
                errors.append(f"wave dataset: {exc}")

        if "chlorophyll_mg_m3" in requested:
            try:
                value = self._fetch_chlorophyll_data(copernicusmarine=copernicusmarine, request=request)
                if value:
                    data_parts.append(value)
            except Exception as exc:
                errors.append(f"chlorophyll dataset: {exc}")

        physics_done: set[str] = set()
        for canonical in [item for item in requested if item in _PHYSICS_VARIABLES]:
            if canonical in physics_done:
                continue
            try:
                value = self._fetch_physics_data(copernicusmarine=copernicusmarine, request=request, canonical=canonical)
                if value:
                    data_parts.append(value)
            except Exception as exc:
                errors.append(f"{canonical} dataset: {exc}")
            if canonical in {"sst_c", "temperature_c"}:
                physics_done.update({"sst_c", "temperature_c"})
            else:
                physics_done.add(canonical)

        if not data_parts:
            return {"status": "unavailable", "error": "No requested Copernicus marine variable could be retrieved.", "details": errors}
        return {"status": "success", "data_parts": data_parts, "errors": errors}


copernicus_provider = CopernicusMarineProvider()
