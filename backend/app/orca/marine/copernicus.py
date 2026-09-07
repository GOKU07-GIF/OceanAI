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

_CHL_VARIABLES = {
    "chlorophyll_mg_m3": "CHL",
}

_PHYSICS_VARIABLES = {
    "sst_c": (COPERNICUS_TEMP_DATASET_ID, "thetao"),
    "temperature_c": (COPERNICUS_TEMP_DATASET_ID, "thetao"),
    "salinity_psu": (COPERNICUS_SALINITY_DATASET_ID, "so"),
}


class CopernicusMarineProvider:
    """Copernicus Marine adapter used by ORCA.

    Supports wave, chlorophyll, near-surface temperature and near-surface
    salinity. Environment credentials are optional because the
    copernicusmarine package can use the credential file created by
    `copernicusmarine login`.
    """

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
        latitude_degrees = radius_km / 111.0
        longitude_degrees = radius_km / 104.0
        return latitude_degrees, longitude_degrees

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

        minimum_longitude = longitude
        maximum_longitude = longitude
        minimum_latitude = latitude
        maximum_latitude = latitude

        if search_radius_km is not None and search_radius_km > 0:
            lat_padding, lon_padding = self._degrees_for_km(search_radius_km)
            minimum_longitude = max(-180.0, longitude - lon_padding)
            maximum_longitude = min(180.0, longitude + lon_padding)
            minimum_latitude = max(-90.0, latitude - lat_padding)
            maximum_latitude = min(90.0, latitude + lat_padding)

        kwargs: dict[str, Any] = {
            "dataset_id": dataset_id,
            "variables": variables,
            "minimum_longitude": minimum_longitude,
            "maximum_longitude": maximum_longitude,
            "minimum_latitude": minimum_latitude,
            "maximum_latitude": maximum_latitude,
            "coordinates_selection_method": (
                "outside" if search_radius_km is not None else "nearest"
            ),
        }

        if search_radius_km is not None and search_radius_km > 0:
            # The fallback is an area-over-a-few-time-steps query, which is
            # the use case Copernicus documents for the Geo Series service.
            kwargs["service"] = "geoseries"

        username, password = self._credentials()
        if username and password:
            kwargs["username"] = username
            kwargs["password"] = password
        # Otherwise let copernicusmarine load its saved credential file.

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
            kwargs["start_datetime"] = (
                now - timedelta(days=recent_observation_days)
            ).isoformat()
            kwargs["end_datetime"] = now.isoformat()
        elif not start_time and not end_time:
            now = datetime.now(timezone.utc)
            kwargs["start_datetime"] = (
                now - timedelta(days=1)
            ).isoformat()
            kwargs["end_datetime"] = now.isoformat()

        return copernicusmarine.open_dataset(**kwargs)

    @staticmethod
    def _distance_km(
        latitude_1: float,
        longitude_1: float,
        latitude_2: float,
        longitude_2: float,
    ) -> float:
        lat1 = math.radians(latitude_1)
        lat2 = math.radians(latitude_2)
        dlat = lat2 - lat1
        dlon = math.radians(longitude_2 - longitude_1)
        a = (
            math.sin(dlat / 2.0) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0) ** 2
        )
        return 6371.0 * 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(1.0 - a, 0.0)))

    def _has_valid_wave_value(
        self,
        selected: Any,
        requested: list[str],
    ) -> bool:
        for canonical in requested:
            provider_key = _WAVE_VARIABLES[canonical]
            if provider_key not in selected.variables:
                continue
            value = self._scalar(selected[provider_key].values)
            if value is not None:
                return True
        return False

    def _nearest_valid_wave_point(
        self,
        dataset: Any,
        requested: list[str],
        requested_latitude: float,
        requested_longitude: float,
    ) -> Any | None:
        if "latitude" not in dataset.coords or "longitude" not in dataset.coords:
            return None

        latitude_values = np.asarray(dataset["latitude"].values).reshape(-1)
        longitude_values = np.asarray(dataset["longitude"].values).reshape(-1)
        if latitude_values.size == 0 or longitude_values.size == 0:
            return None

        candidate_pairs: list[tuple[float, float, float]] = []
        for candidate_latitude in latitude_values:
            for candidate_longitude in longitude_values:
                distance = self._distance_km(
                    requested_latitude,
                    requested_longitude,
                    float(candidate_latitude),
                    float(candidate_longitude),
                )
                candidate_pairs.append((distance, float(candidate_latitude), float(candidate_longitude)))

        candidate_pairs.sort(key=lambda item: item[0])

        for _, candidate_latitude, candidate_longitude in candidate_pairs:
            try:
                selected = dataset.sel(
                    latitude=candidate_latitude,
                    longitude=candidate_longitude,
                    method="nearest",
                )
                if "time" in selected.dims:
                    selected = selected.isel(time=-1)
                if self._has_valid_wave_value(selected, requested):
                    return selected
            except Exception:
                continue

        return None

    def _fetch_wave_data(
        self,
        *,
        copernicusmarine: Any,
        request: MarineDataRequest,
        requested: list[str],
    ) -> dict[str, Any] | None:
        requested_latitude = float(request["latitude"])
        requested_longitude = float(request["longitude"])

        dataset = self._open_dataset(
            copernicusmarine=copernicusmarine,
            dataset_id=self.wave_dataset_id,
            variables=[_WAVE_VARIABLES[item] for item in requested],
            request=request,
        )

        selected = dataset.sel(
            latitude=requested_latitude,
            longitude=requested_longitude,
            method="nearest",
        )

        if "time" in selected.dims:
            selected = selected.isel(time=-1)

        search_radius_km = float(request.get("radius_km", 50.0) or 50.0)
        snapped_to_ocean = False

        if not self._has_valid_wave_value(selected, requested):
            try:
                dataset.close()
            except Exception:
                pass

            dataset = self._open_dataset(
                copernicusmarine=copernicusmarine,
                dataset_id=self.wave_dataset_id,
                variables=[_WAVE_VARIABLES[item] for item in requested],
                request=request,
                search_radius_km=search_radius_km,
            )
            selected = self._nearest_valid_wave_point(
                dataset,
                requested,
                requested_latitude,
                requested_longitude,
            )
            if selected is None:
                try:
                    dataset.close()
                except Exception:
                    pass
                return None
            snapped_to_ocean = True

        timestamp = (
            str(selected["time"].values)
            if "time" in selected.coords
            else datetime.now(timezone.utc).isoformat()
        )

        selected_latitude = float(selected.latitude.values)
        selected_longitude = float(selected.longitude.values)
        distance_km = self._distance_km(
            requested_latitude,
            requested_longitude,
            selected_latitude,
            selected_longitude,
        )

        result: dict[str, Any] = {
            "source": "Copernicus Marine",
            "dataset": self.wave_dataset_id,
            "type": "forecast",
            "location": {
                "latitude": selected_latitude,
                "longitude": selected_longitude,
            },
            "timestamp": timestamp,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "quality": "provider-dataset",
            "metadata": {
                "dataset_id": self.wave_dataset_id,
                "variables": [_WAVE_VARIABLES[item] for item in requested],
                "requested_location": {
                    "latitude": requested_latitude,
                    "longitude": requested_longitude,
                },
                "location_snap_distance_km": distance_km,
                "snapped_to_nearest_valid_ocean_cell": snapped_to_ocean,
            },
        }

        for canonical, provider_key in _WAVE_VARIABLES.items():
            if canonical not in requested:
                continue
            if provider_key not in selected.variables:
                continue

            value = self._scalar(selected[provider_key].values)
            if value is not None:
                result[canonical] = value

        if not self._has_valid_wave_value(selected, requested):
            return None

        return result

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
            recent_observation_days=8,
        )

        selected = dataset.sel(
            latitude=request["latitude"],
            longitude=request["longitude"],
            method="nearest",
        )

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
                "note": "Latest available near-real-time ocean-colour observation; not a forecast.",
            },
        }

    def _fetch_physics_data(
        self,
        *,
        copernicusmarine: Any,
        request: MarineDataRequest,
        canonical: str,
    ) -> dict[str, Any] | None:
        dataset_id, provider_variable = _PHYSICS_VARIABLES[canonical]

        dataset = self._open_dataset(
            copernicusmarine=copernicusmarine,
            dataset_id=dataset_id,
            variables=[provider_variable],
            request=request,
            minimum_depth=0.5,
            maximum_depth=200.0,
        )

        selected = dataset.sel(
            latitude=request["latitude"],
            longitude=request["longitude"],
            method="nearest",
        )

        value, timestamp, depth_m = self._latest_valid_scalar(
            selected,
            provider_variable,
        )

        if value is None:
            return None

        latitude = float(selected.latitude.values)
        longitude = float(selected.longitude.values)
        retrieved_at = datetime.now(timezone.utc).isoformat()

        data: dict[str, Any] = {
            "source": "Copernicus Marine",
            "dataset": dataset_id,
            "type": "forecast",
            "location": {
                "latitude": latitude,
                "longitude": longitude,
            },
            "timestamp": timestamp or retrieved_at,
            "retrieved_at": retrieved_at,
            "depth_m": depth_m,
            "quality": "provider-dataset",
            "metadata": {
                "dataset_id": dataset_id,
                "variable": provider_variable,
                "depth_m": depth_m,
            },
        }

        if canonical in {"sst_c", "temperature_c"}:
            data["sst_c"] = value
            data["temperature_c"] = value
            data["metadata"]["note"] = (
                "Near-surface Copernicus model potential temperature "
                "used as a surface-temperature proxy; not a satellite SST measurement."
            )
        else:
            data["salinity_psu"] = value
            data["metadata"]["note"] = (
                "Near-surface Copernicus model salinity from the latest "
                "valid shallow ocean level."
            )

        return data

    def fetch(
        self,
        request: MarineDataRequest,
    ) -> dict[str, Any]:
        supported = set(_WAVE_VARIABLES) | set(_CHL_VARIABLES) | set(_PHYSICS_VARIABLES)
        requested = [
            item
            for item in request.get("variables", [])
            if item in supported
        ]

        if not requested:
            return {
                "status": "unavailable",
                "error": "Copernicus adapter does not support the requested marine variables.",
            }

        if request.get("latitude") is None or request.get("longitude") is None:
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

        data_parts: list[dict[str, Any]] = []
        errors: list[str] = []

        wave_requested = [item for item in requested if item in _WAVE_VARIABLES]
        if wave_requested:
            try:
                value = self._fetch_wave_data(
                    copernicusmarine=copernicusmarine,
                    request=request,
                    requested=wave_requested,
                )
                if value:
                    data_parts.append(value)
            except Exception as exc:
                errors.append(f"wave dataset: {exc}")

        if "chlorophyll_mg_m3" in requested:
            try:
                value = self._fetch_chlorophyll_data(
                    copernicusmarine=copernicusmarine,
                    request=request,
                )
                if value:
                    data_parts.append(value)
            except Exception as exc:
                errors.append(f"chlorophyll dataset: {exc}")

        physics_requested = [
            item
            for item in requested
            if item in _PHYSICS_VARIABLES
        ]
        physics_done: set[str] = set()

        for canonical in physics_requested:
            # `sst_c` and `temperature_c` map to the same thetao dataset.
            if canonical in physics_done:
                continue

            try:
                value = self._fetch_physics_data(
                    copernicusmarine=copernicusmarine,
                    request=request,
                    canonical=canonical,
                )
                if value:
                    data_parts.append(value)
            except Exception as exc:
                errors.append(
                    f"{canonical} dataset: {exc}"
                )

            if canonical in {"sst_c", "temperature_c"}:
                physics_done.update({"sst_c", "temperature_c"})
            else:
                physics_done.add(canonical)

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
