from __future__ import annotations

from typing import Any, Literal, TypedDict


MARINE_VARIABLES = (
    "wave_height_m",
    "swell_height_m",
    "wave_period_s",
    "current_speed_ms",
    "current_direction_deg",
    "sst_c",
    "chlorophyll_mg_m3",
    "pfz_available",
    "advisories",
)


class MarineLocation(TypedDict):
    latitude: float
    longitude: float


class MarineAdvisory(TypedDict, total=False):
    title: str
    severity: str
    issued_at: str
    valid_until: str
    source: str
    description: str


class MarineDataRequest(TypedDict, total=False):
    """Normalized request sent to a marine data provider."""

    latitude: float
    longitude: float
    start_time: str
    end_time: str
    variables: list[str]
    radius_km: float


class MarineConditions(TypedDict, total=False):
    """Canonical marine observation/forecast shape used by ORCA.

    Providers may return a subset of fields. Missing fields must remain
    missing/null; callers must never infer an unsafe-data value from absence.
    """

    source: str
    dataset: str
    type: Literal["forecast", "observation", "advisory", "mixed"]
    location: MarineLocation
    timestamp: str
    retrieved_at: str
    wave_height_m: float
    swell_height_m: float
    wave_period_s: float
    current_speed_ms: float
    current_direction_deg: float
    sst_c: float
    chlorophyll_mg_m3: float
    pfz_available: bool
    advisories: list[MarineAdvisory]
    quality: str
    metadata: dict[str, Any]
