"""Verify configured INCOIS ERDDAP datasets before acquisition.

The verifier performs small metadata/sample requests only. It does not claim a
full archive is downloadable. Results are written as JSON for CI inspection.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import quote

import requests

BASE_URL = "https://erddap.incois.gov.in/erddap"

DATASETS = {
    "sst": {
        "dataset_id": "NOAA_AVHRR_AMSR_datasets",
        "sample_query": "sst[0][0][0][0]",
    },
    "value_added": {
        "dataset_id": "incois_valueadded_products_datasets",
        "sample_query": "MLD[0][0][0]",
    },
    "quickscat": {
        "dataset_id": "incois_quickscat_daily_datasets",
        "sample_query": "WIND_SPEED[0][0][0]",
    },
    "oceansat2": {
        "dataset_id": "incois_oceansat2_datasets",
        "sample_query": "CHL[0][0][0]",
    },
    "argo_vam": {
        "dataset_id": "incois_argo_mnt_VAM",
        "sample_query": "TEMP[0][0][0][0]",
    },
}


def request(url: str, timeout: int = 30) -> tuple[bool, int, str]:
    try:
        response = requests.get(url, timeout=timeout)
        return response.ok, response.status_code, response.text[:500]
    except requests.RequestException as exc:
        return False, 0, str(exc)


def verify_dataset(alias: str, config: dict) -> dict:
    dataset_id = config["dataset_id"]
    urls = {
        "info": f"{BASE_URL}/info/{dataset_id}/index.json",
        "das": f"{BASE_URL}/griddap/{dataset_id}.das",
        "sample": f"{BASE_URL}/griddap/{dataset_id}.csv?{quote(config['sample_query'], safe='[]')}",
    }

    checks = {}
    for name, url in urls.items():
        ok, status, detail = request(url)
        checks[name] = {"ok": ok, "status": status, "detail": detail}

    return {
        "alias": alias,
        "dataset_id": dataset_id,
        "checks": checks,
        "status": "available" if all(item["ok"] for item in checks.values()) else "needs_review",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("datasets/raw/incois/source_verification.json"))
    args = parser.parse_args()

    results = [verify_dataset(alias, config) for alias, config in DATASETS.items()]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")

    for result in results:
        print(f"{result['alias']}: {result['status']} ({result['dataset_id']})")

    if not any(result["status"] == "available" for result in results):
        raise SystemExit("No configured INCOIS dataset passed all source checks")


if __name__ == "__main__":
    main()
