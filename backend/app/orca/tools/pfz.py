from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

import requests


PFZ_WEBGIS_URL = "https://incois.gov.in/MarineFisheries/PfzWebGis"
PFZ_TEXT_URL = "https://incois.gov.in/MarineFisheries/TextDataHome?mfid=1&request_locale=en"

_COORDINATE_PATTERN = re.compile(
    r"(?P<lat>[-+]?\d{1,2}(?:\.\d+)?)\s*(?:°\s*)?(?P<lat_dir>[NS])"
    r"\s*[,;/ ]+\s*"
    r"(?P<lon>[-+]?\d{2,3}(?:\.\d+)?)\s*(?:°\s*)?(?P<lon_dir>[EW])",
    re.IGNORECASE,
)
_DATE_RANGE_PATTERN = re.compile(
    r"(?P<start>\d{1,2}\s+[A-Za-z]{3}\s+\d{4})\s*"
    r"(?P<end>\d{1,2}\s+[A-Za-z]{3}\s+\d{4})",
    re.IGNORECASE,
)


def _signed_coordinate(value: str, direction: str) -> float:
    number = float(value)
    return -number if direction.upper() in {"S", "W"} else number


def _extract_coordinates(text: str) -> list[dict[str, float]]:
    coordinates: list[dict[str, float]] = []
    seen: set[tuple[float, float]] = set()

    for match in _COORDINATE_PATTERN.finditer(text):
        lat = _signed_coordinate(match.group("lat"), match.group("lat_dir"))
        lon = _signed_coordinate(match.group("lon"), match.group("lon_dir"))
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            continue
        key = (round(lat, 6), round(lon, 6))
        if key in seen:
            continue
        seen.add(key)
        coordinates.append({"latitude": lat, "longitude": lon})

    return coordinates


def _visible_text(html: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", html, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(text.split())


def get_pfz_advisory(
    *,
    sector: str | None = None,
    language: str = "en",
    timeout_seconds: float = 10.0,
) -> dict[str, Any]:
    """Read the public INCOIS PFZ text page and preserve explicit advisory facts.

    INCOIS documents PFZ maps/text with geo-referenced locations, but the public
    page can expose a form shell rather than the selected sector's point list.
    Therefore this adapter returns exact coordinates only when they are
    explicitly present in the fetched response; it never invents them.
    """
    url = PFZ_TEXT_URL.replace("request_locale=en", f"request_locale={language or 'en'}")

    try:
        response = requests.get(
            url,
            timeout=timeout_seconds,
            headers={"User-Agent": "OceanAI-ORCA/1.0"},
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return {
            "status": "unavailable",
            "source": "INCOIS",
            "dataset": "PFZ Text Advisory",
            "type": "advisory",
            "sector": sector,
            "language": language or "en",
            "error": f"INCOIS PFZ text request failed: {exc}",
            "webgis_url": PFZ_WEBGIS_URL,
            "text_url": url,
        }

    text = _visible_text(response.text)
    coordinates = _extract_coordinates(text)

    advisory_date = None
    valid_until = None
    date_match = _DATE_RANGE_PATTERN.search(text)
    if date_match:
        advisory_date = date_match.group("start")
        valid_until = date_match.group("end")

    retrieved_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    result: dict[str, Any] = {
        "status": "success",
        "source": "INCOIS",
        "dataset": "PFZ Text Advisory",
        "type": "advisory",
        "sector": sector,
        "language": language or "en",
        "advisory_date": advisory_date,
        "valid_until": valid_until,
        "retrieved_at": retrieved_at,
        "pfz_available": bool(coordinates) or bool(advisory_date),
        "locations": coordinates,
        "webgis_url": PFZ_WEBGIS_URL,
        "text_url": url,
        "quality": "public-page-best-effort",
        "metadata": {
            "note": (
                "INCOIS states that PFZ text contains latitude/longitude, depth, "
                "distance and direction from prominent coastal sites. Exact point "
                "data is returned only when explicitly exposed by the fetched page."
            )
        },
    }

    if not coordinates:
        result["location_warning"] = (
            "The public response did not expose explicit PFZ coordinates. "
            "Use the INCOIS WebGIS/text product for exact current PFZ locations."
        )

    return result


def get_pfz_service_status(*, timeout_seconds: float = 10.0) -> dict[str, Any]:
    """Verify reachability of both official INCOIS PFZ delivery pages."""
    errors: list[str] = []
    reachable: dict[str, bool] = {}

    for name, url in (("webgis", PFZ_WEBGIS_URL), ("text", PFZ_TEXT_URL)):
        try:
            response = requests.get(
                url,
                timeout=timeout_seconds,
                headers={"User-Agent": "OceanAI-ORCA/1.0"},
            )
            reachable[name] = response.ok
            if not response.ok:
                errors.append(f"{name} endpoint returned HTTP {response.status_code}.")
        except requests.RequestException as exc:
            reachable[name] = False
            errors.append(f"{name} endpoint request failed: {exc}")

    return {
        "status": "success" if any(reachable.values()) else "unavailable",
        "source": "INCOIS",
        "dataset": "Potential Fishing Zone Advisory WebGIS",
        "type": "advisory",
        "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "service_urls": {"webgis": PFZ_WEBGIS_URL, "text": PFZ_TEXT_URL},
        "reachable": reachable,
        "note": "Reachability check only; exact PFZ coordinates are not inferred from service availability.",
        "errors": errors,
    }
