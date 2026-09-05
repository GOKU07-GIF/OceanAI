"""Run the INCOIS core acquisition in one Python process on Windows.

This wrapper installs Truststore's native certificate handling before importing
requests/xarray-based acquisition code. It also avoids child-process SSL
configuration problems in the original acquisition runner.

Usage:
    python -m pip install truststore
    python scripts/python/run_incois_core_windows.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import truststore

truststore.inject_into_ssl()

ROOT = Path(__file__).resolve().parents[2]
scripts_dir = ROOT / "scripts" / "python"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

import download_incois_erddap as downloader

BATCHES = [
    ("sst", "2011-10-02T00:00:00Z", "2011-10-04T00:00:00Z"),
    ("value_added", "2019-03-28T00:00:00Z", "2019-03-30T00:00:00Z"),
    ("quickscat", "2009-11-19T00:00:00Z", "2009-11-21T00:00:00Z"),
    ("oceansat2", "2020-04-29T00:00:00Z", "2020-05-01T00:00:00Z"),
    ("argo_vam", "2026-07-13T00:00:00Z", "2026-07-15T00:00:00Z"),
]


def run_one(dataset: str, start: str, end: str) -> None:
    argv = [
        "download_incois_erddap.py",
        "--dataset", dataset,
        "--start", start,
        "--end", end,
        "--min-lon", "68.0",
        "--max-lon", "78.0",
        "--min-lat", "8.0",
        "--max-lat", "24.0",
        "--min-depth", "5.0",
        "--max-depth", "200.0",
        "--format", "parquet",
        "--output-dir", str(ROOT / "datasets" / "raw" / "incois"),
    ]
    old_argv = sys.argv
    try:
        sys.argv = argv
        downloader.main()
    finally:
        sys.argv = old_argv


def main() -> None:
    failures = 0
    for dataset, start, end in BATCHES:
        print(f"\n=== {dataset}: {start} -> {end} ===")
        try:
            run_one(dataset, start, end)
            print(f"OK: {dataset}")
        except Exception as exc:
            failures += 1
            print(f"FAILED: {dataset}: {exc}")
            print("Continuing with the next dataset.")

    if failures:
        raise SystemExit(f"{failures} dataset batch(es) failed")
    print("\nAll configured INCOIS core batches completed.")


if __name__ == "__main__":
    main()
