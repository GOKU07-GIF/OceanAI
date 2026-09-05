"""Verify configured INCOIS ERDDAP datasets before acquisition.

The verifier performs small metadata/sample requests only. It checks that the
published dataset exposes the variables we intend to download and writes the
results as JSON for CI inspection. It does not claim a full archive is
available or downloadable.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import requests

BASE_URL = "https://erddap.incois.gov.in/erddap"

DATASETS = {
    "sst": {
        "dataset_id": "NOAA_AVHRR_AMSR_datasets",
        "variables": ["sst", "anom"],
    },
    "value_added": {
        "dataset_id": "incois_valueadded_products_datasets",
        "variables": ["MLD", "ILD", "D26", "D20", "GEO_U", "GEO_V"],
    },
    "quickscat": {
        "dataset_id": "incois_quickscat_daily_datasets",
        "variables": [
            "WIND_SPEED", "ZONAL_WIND_SPEED", "MERI_WIND_SPEED",
            "WIND_STRESS", "ZONAL_WIND_STRESS", "MERI_WIND_STRESS",
            "WIND_STRESS_CURL",
        ],
    },
    "oceansat2": {
        "dataset_id": "incois_oceansat2_datasets",
        "variables": ["CHL", "KD490", "TSM"],
    },
    "argo_vam": {
        "dataset_id": "incois_argo_mnt_VAM",
        "variables": ["TEMP", "TERR", "SAL", "SERR"],
    },
}


def request(url: str, timeout: int = 30) -> tuple[bool, int, str]:
    try:
        response = requests.get(url, timeout=timeout)
        return response.ok, response.status_code, response.text
    except requests.RequestException as exc:
        return False, 0, str(exc)


def verify_dataset(alias: str, config: dict) -> dict:
    dataset_id = config["dataset_id"]
    metadata_url = f"{BASE_URL}/info/{dataset_id}/index.json"
    das_url = f"{BASE_URL}/griddap/{dataset_id}.das"

    metadata_ok, metadata_status, metadata_text = request(metadata_url)
    das_ok, das_status, das_text = request(das_url)

    variable_checks = {
        variable: bool(re.search(rf"\b{re.escape(variable)}\s*\{{", das_text))
        for variable in config["variables"]
    }

    dimensions_detected = []
    if metadata_ok:
        try:
            payload = json.loads(metadata_text)
            if isinstance(payload, list):
                dimensions_detected = [
                    str(item.get("name"))
                    for item in payload
                    if isinstance(item, dict) and item.get("type") == "dimension"
                ]
        except json.JSONDecodeError:
            dimensions_detected = []

    all_variables_ok = all(variable_checks.values()) if variable_checks else False
    status = "available" if metadata_ok and das_ok and all_variables_ok else "needs_review"

    return {
        "alias": alias,
        "dataset_id": dataset_id,
        "checks": {
            "metadata": {"ok": metadata_ok, "status": metadata_status},
            "das": {"ok": das_ok, "status": das_status},
            "variables": variable_checks,
            "dimensions_detected": dimensions_detected,
        },
        "status": status,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("datasets/raw/incois/source_verification.json"))
    args = parser.parse_args()

    results = [verify_dataset(alias, config) for alias, config in DATASETS.items()]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")

    passed = 0
    for result in results:
        if result["status"] == "available":
            passed += 1
        print(f"{result['alias']}: {result['status']} ({result['dataset_id']})")
        for variable, ok in result["checks"]["variables"].items():
            print(f"  {variable}: {'OK' if ok else 'MISSING'}")

    if passed == 0:
        raise SystemExit("No configured INCOIS dataset passed source checks")


if __name__ == "__main__":
    main()
