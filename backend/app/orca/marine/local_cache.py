from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import xarray as xr


DEFAULT_MAX_DISTANCE_KM = 75.0
DEFAULT_MAX_DEPTH_M = 10.0


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
    return 6371.0 * 2.0 * math.atan2(
        math.sqrt(a),
        math.sqrt(max(1.0 - a, 0.0)),
    )


def _repository_root() -> Path:
    # backend/app/orca/marine/local_cache.py -> repository root
    return Path(__file__).resolve().parents[4]


def _candidate_files() -> list[Path]:
    directory = _repository_root() / "datasets" / "raw" / "copernicus"
    if not directory.exists():
        return []
    return sorted(
        directory.glob("*thetao*.nc"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )


def _latest_valid_thetao(
    dataset: xr.Dataset,
    latitude: float,
    longitude: float,
    max_distance_km: float,
    max_depth_m: float,
) -> dict[str, Any] | None:
    if "thetao" not in dataset.data_vars:
        return None
    if "latitude" not in dataset.coords or "longitude" not in dataset.coords:
        return None

    latitude_values = np.asarray(dataset["latitude"].values).reshape(-1)
    longitude_values = np.asarray(dataset["longitude"].values).reshape(-1)
    if latitude_values.size == 0 or longitude_values.size == 0:
        return None

    candidates: list[tuple[float, float, float]] = []
    for candidate_latitude in latitude_values:
        for candidate_longitude in longitude_values:
            distance = _distance_km(
                latitude,
                longitude,
                float(candidate_latitude),
                float(candidate_longitude),
            )
            if distance <= max_distance_km:
                candidates.append(
                    (
                        distance,
                        float(candidate_latitude),
                        float(candidate_longitude),
                    )
                )

    candidates.sort(key=lambda item: item[0])
    if not candidates:
        return None

    times = (
        np.asarray(dataset["time"].values).reshape(-1)
        if "time" in dataset.coords
        else np.asarray([np.datetime64("NaT")])
    )

    if "depth" in dataset.coords:
        depth_values = np.asarray(dataset["depth"].values).reshape(-1)
    else:
        depth_values = np.asarray([0.0])

    allowed_depth_indices = [
        index
        for index, depth in enumerate(depth_values)
        if math.isfinite(float(depth)) and float(depth) <= max_depth_m
    ]
    if not allowed_depth_indices:
        return None
    allowed_depth_indices.sort(key=lambda index: float(depth_values[index]))

    thetao = dataset["thetao"]

    # Search nearest spatially first, then newest valid forecast time, then
    # shallowest valid level. Never synthesize a value from invalid cells.
    for distance, candidate_latitude, candidate_longitude in candidates:
        try:
            selected = thetao.sel(
                latitude=candidate_latitude,
                longitude=candidate_longitude,
                method="nearest",
            )
        except Exception:
            continue

        values = np.asarray(selected.values)

        if "time" in selected.dims and "depth" in selected.dims:
            time_axis = selected.dims.index("time")
            depth_axis = selected.dims.index("depth")
            values = np.moveaxis(values, (time_axis, depth_axis), (0, 1))
        elif "time" in selected.dims:
            time_axis = selected.dims.index("time")
            values = np.moveaxis(values, time_axis, 0)[:, None]
        elif "depth" in selected.dims:
            depth_axis = selected.dims.index("depth")
            values = np.moveaxis(values, depth_axis, 0)[None, :]
        else:
            values = np.asarray(values).reshape(1, 1)

        for time_index in range(values.shape[0] - 1, -1, -1):
            for depth_index in allowed_depth_indices:
                if depth_index >= values.shape[1]:
                    continue
                try:
                    value = float(values[time_index, depth_index])
                except (TypeError, ValueError):
                    continue
                if not math.isfinite(value):
                    continue

                dataset_timestamp = (
                    str(times[time_index])
                    if time_index < times.size
                    else datetime.now(timezone.utc).isoformat()
                )
                return {
                    "sst_c": value,
                    "source": "Copernicus Marine",
                    "dataset": str(
                        dataset.attrs.get(
                            "title",
                            dataset.attrs.get(
                                "product",
                                "Copernicus thetao local NetCDF cache",
                            ),
                        )
                    ),
                    "dataset_id": dataset.attrs.get("product")
                    or dataset.attrs.get("dataset_id")
                    or "thetao",
                    "timestamp": dataset_timestamp,
                    "location": {
                        "latitude": candidate_latitude,
                        "longitude": candidate_longitude,
                    },
                    "distance_km": round(distance, 2),
                    "depth_m": float(depth_values[depth_index]),
                    "data_type": "cached_copernicus_forecast",
                    "quality": "provider-dataset",
                    "note": (
                        "Near-surface Copernicus model potential temperature "
                        "from the local NetCDF cache, used as an SST proxy; "
                        "not a satellite SST measurement."
                    ),
                }

    return None


def get_cached_copernicus_sst(
    *,
    latitude: float,
    longitude: float,
    max_distance_km: float = DEFAULT_MAX_DISTANCE_KM,
    max_depth_m: float = DEFAULT_MAX_DEPTH_M,
) -> dict[str, Any] | None:
    """Read the newest valid near-surface thetao value from local Copernicus files."""
    for path in _candidate_files():
        dataset: xr.Dataset | None = None
        try:
            dataset = xr.open_dataset(path)
            result = _latest_valid_thetao(
                dataset,
                latitude=latitude,
                longitude=longitude,
                max_distance_km=max_distance_km,
                max_depth_m=max_depth_m,
            )
            if result is not None:
                result["file"] = str(path)
                result["retrieved_at"] = datetime.now(timezone.utc).isoformat()
                return result
        except Exception:
            continue
        finally:
            if dataset is not None:
                try:
                    dataset.close()
                except Exception:
                    pass

    return None
