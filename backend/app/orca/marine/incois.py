from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote

import requests

from app.orca.marine.models import MarineDataRequest


INCOIS_ERDDAP_BASE_URL = "https://erddap.incois.gov.in/erddap"
INCOIS_SST_DATASET_ID = "incois_argo_sst_weekly"
INCOIS_SST_VARIABLE = "ASST"


class INCOISERDDAPSSTProvider:
    """INCOIS ERDDAP adapter for the latest available ARGO-derived SST.

    The dataset is observational/analysis context, not a future forecast. The
    adapter therefore never labels its SST as a forecast for a requested future
    time window.
    """

    name = "incois"

    def __init__(
        self,
        *,
        base_url: str = INCOIS_ERDDAP_BASE_URL,
        dataset_id: str = INCOIS_SST_DATASET_ID,
        timeout_seconds: float = 12.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.dataset_id = dataset_id
        self.timeout_seconds = timeout_seconds

    def fetch(self, request: MarineDataRequest) -> dict[str, Any]:
        variables = request.get("variables", [])
        if variables and "sst_c" not in variables:
            return {
                "status": "unavailable",
                "error": "INCOIS adapter currently supports only sst_c.",
            }

        latitude = request.get("latitude")
        longitude = request.get("longitude")
        if latitude is None or longitude is None:
            return {
                "status": "unavailable",
                "error": "Latitude and longitude are required for the INCOIS SST lookup.",
            }

        # ERDDAP griddap supports [last] for the most recent time value and
        # parenthesized dimension values for the closest available grid point.
        query = (
            f"{INCOIS_SST_VARIABLE}"
            f"[last]"
            f"[{latitude}]"
            f"[{longitude}]"
        )
        url = (
            f"{self.base_url}/griddap/"
            f"{quote(self.dataset_id, safe='')}.json?{query}"
        )

        try:
            response = requests.get(url, timeout=self.timeout_seconds)
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            return {
                "status": "unavailable",
                "error": f"INCOIS ERDDAP request failed: {exc}",
            }

        table = payload.get("table")
        if not isinstance(table, dict):
            return {
                "status": "unavailable",
                "error": "INCOIS ERDDAP returned an unexpected response shape.",
            }

        column_names = table.get("columnNames")
        rows = table.get("rows")
        if not isinstance(column_names, list) or not isinstance(rows, list) or not rows:
            return {
                "status": "unavailable",
                "error": "No INCOIS SST observation was returned for the requested location.",
            }

        first_row = rows[0]
        if not isinstance(first_row, list):
            return {
                "status": "unavailable",
                "error": "INCOIS ERDDAP returned an invalid row payload.",
            }

        record = dict(zip(column_names, first_row))
        sst_value = record.get(INCOIS_SST_VARIABLE)
        if not isinstance(sst_value, (int, float)):
            return {
                "status": "unavailable",
                "error": "INCOIS returned a missing/non-numeric SST value.",
            }

        dataset_time = record.get("time")
        retrieved_at = datetime.now(timezone.utc).isoformat()

        data: dict[str, Any] = {
            "source": "INCOIS",
            "dataset": f"{self.dataset_id}.ERDDAP",
            "type": "observation",
            "location": {
                "latitude": float(record.get("latitude", latitude)),
                "longitude": float(record.get("longitude", longitude)),
            },
            "timestamp": str(dataset_time) if dataset_time is not None else retrieved_at,
            "retrieved_at": retrieved_at,
            "sst_c": float(sst_value),
            "quality": "dataset-provided",
            "metadata": {
                "endpoint": url,
                "variable": INCOIS_SST_VARIABLE,
                "dataset_id": self.dataset_id,
                "note": "Latest available INCOIS ARGO SST context; not a future forecast.",
            },
        }

        return {
            "status": "success",
            "data": data,
        }


incois_provider = INCOISERDDAPSSTProvider()
