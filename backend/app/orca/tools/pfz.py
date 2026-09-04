from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import requests


PFZ_WEBGIS_URL = "https://incois.gov.in/MarineFisheries/PfzWebGis"
PFZ_TEXT_URL = "https://incois.gov.in/MarineFisheries/TextDataHome?mfid=1&request_locale=en"


def get_pfz_service_status(*, timeout_seconds: float = 10.0) -> dict[str, Any]:
    """Verify that the official INCOIS PFZ service is reachable.

    This intentionally does not fabricate PFZ coordinates. The official
    WebGIS exposes the current geo-referenced advisory map; precise point
    extraction will be added only when a stable public machine-readable
    endpoint is verified.
    """
    errors: list[str] = []
    reachable: dict[str, bool] = {}

    for name, url in (("webgis", PFZ_WEBGIS_URL), ("text", PFZ_TEXT_URL)):
        try:
            response = requests.get(url, timeout=timeout_seconds)
            reachable[name] = response.ok
            if not response.ok:
                errors.append(f"{name} endpoint returned HTTP {response.status_code}.")
        except requests.RequestException as exc:
            reachable[name] = False
            errors.append(f"{name} endpoint request failed: {exc}")

    status = "success" if any(reachable.values()) else "unavailable"

    return {
        "status": status,
        "source": "INCOIS",
        "dataset": "Potential Fishing Zone Advisory WebGIS",
        "type": "advisory",
        "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "service_urls": {
            "webgis": PFZ_WEBGIS_URL,
            "text": PFZ_TEXT_URL,
        },
        "reachable": reachable,
        "note": (
            "INCOIS provides current PFZ information through its WebGIS/text services. "
            "This adapter verifies service availability but does not infer PFZ coordinates."
        ),
        "errors": errors,
    }
