from __future__ import annotations

from typing import Any

import requests


NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
USER_AGENT = "OceanAI-ORCA/1.0 (marine decision support prototype)"


def reverse_geocode(*, latitude: float, longitude: float) -> dict[str, Any]:
    """Resolve coordinates into human-readable OpenStreetMap place context.

    This tool deliberately reports the source and does not infer maritime
    boundaries or restrictions that are not returned by the provider.
    """
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        return {
            "status": "error",
            "source": "OpenStreetMap Nominatim",
            "error": "Invalid latitude/longitude.",
        }

    try:
        response = requests.get(
            NOMINATIM_URL,
            params={
                "lat": latitude,
                "lon": longitude,
                "format": "jsonv2",
                "zoom": 10,
            },
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        return {
            "status": "error",
            "source": "OpenStreetMap Nominatim",
            "error": f"Geocoding unavailable: {exc}",
        }

    address = data.get("address", {})
    return {
        "status": "success",
        "source": "OpenStreetMap Nominatim",
        "dataset": "Reverse Geocoding",
        "type": "geospatial_context",
        "location": {
            "latitude": latitude,
            "longitude": longitude,
            "display_name": data.get("display_name"),
            "city": address.get("city") or address.get("town") or address.get("village"),
            "state": address.get("state"),
            "country": address.get("country"),
            "country_code": address.get("country_code"),
        },
        "retrieved_at": data.get("name") is not None and None or None,
        "note": "Boundary, restriction and routing claims require dedicated GIS data; they are not inferred here.",
    }
