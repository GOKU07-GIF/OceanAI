from __future__ import annotations

import math
import os
from datetime import datetime, timedelta, timezone
from typing import Any

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
    ) -> Any:
        latitude = float(request["latitude"])
        longitude = float(request["longitude"])

        kwargs: dict[str, Any] = {
            "dataset_id": dataset_id,
            "variables": variables,
            "minimum_longitude": longitude,
            "maximum_longitude": longitude,
            "minimum_latitude": latitude,
            "maximum_latitude": latitude,
            "coordinates_selection_method": "nearest",
        }

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
    def _latest_valid_scalar(
        dataset: Any,
        variable_name: str,
    ) -> tuple[float | None, str | None, float | None]:
        if variable_name not in dataset.variables:
            return None, None, None

        field = dataset[variable_name]
        has_time = "time" in field.dims
        has_depth = "depth" in field.dims

        time_count = field.sizes["time"] if has_time else 1
        depth_count = field.sizes["depth"] if has_depth else 1

        for time_index in range(time_count - 1, -1, -1):
            for depth_index in range(depth_count):
                indexers: dict[str, int] = {}
                if has_time:
                    indexers["time"] = time_index
                if has_depth:
                    indexers["depth"] = depth_index

                try:
                    raw = field.isel(**indexers).values
                except Exception:
                    continue

                value = CopernicusMarineProvider._scalar(raw)
                if value is None:
                    continue

                timestamp: str | None = None
                if has_time and "time" in dataset.coords:
                    try:
                        timestamp = str(
                            dataset["time"].isel(time=time_index).values
                        )
                    except Exception:
                        pass

                depth_m: float | None = None
                if has_depth and "depth" in dataset.coords:
                    try:
                        depth_m = CopernicusMarineProvider._scalar(
                            dataset["depth"].isel(depth=depth_index).values
                        )
                    except Exception:
                        pass

                return value, timestamp, depth_m

        return None, None, None

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
            selected = selected.isel(time=-1)

        timestamp = (
            str(selected["time"].values)
            if "time" in selected.coords
            else datetime.now(timezone.utc).isoformat()
        )

        result: dict[str, Any] = {
            "source": "Copernicus Marine",
            "dataset": self.wave_dataset_id,
            "type": "forecast",
            "location": {
                "latitude": float(selected.latitude.values),
                "longitude": float(selected.longitude.values),
            },
            "timestamp": timestamp,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "quality": "provider-dataset",
            "metadata": {
                "dataset_id": self.wave_dataset_id,
                "variables": [_WAVE_VARIABLES[item] for item in requested],
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
