from __future__ import annotations

from typing import Any, Sequence

from app.orca.marine.models import MarineDataRequest
from app.orca.marine.provider import marine_provider


def get_marine_conditions(
    *,
    latitude: float,
    longitude: float,
    start_time: str | None = None,
    end_time: str | None = None,
    variables: list[str] | None = None,
    radius_km: float = 50.0,
    provider_order: Sequence[str] = ("incois", "copernicus", "mosdac"),
) -> dict[str, Any]:
    """Fetch marine conditions through the source-agnostic ORCA data layer.

    No provider is assumed to be available. Until an adapter is explicitly
    registered, the tool returns an unavailable result and reports which
    variables are missing instead of manufacturing values.
    """
    request: MarineDataRequest = {
        "latitude": latitude,
        "longitude": longitude,
        "variables": variables or [],
        "radius_km": radius_km,
    }

    if start_time is not None:
        request["start_time"] = start_time
    if end_time is not None:
        request["end_time"] = end_time

    return marine_provider.fetch(
        request=request,
        provider_order=provider_order,
    )
