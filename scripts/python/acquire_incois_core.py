"""Acquire a small, reproducible INCOIS core-data batch.

This runner intentionally uses short time windows instead of mirroring entire
INCOIS archives. Each successful batch is downloaded as NetCDF and can be
transformed to Parquet by the shared ERDDAP downloader.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOWNLOADER = ROOT / "scripts" / "python" / "download_incois_erddap.py"

# These dates are selected from currently documented coverage windows.
BATCHES = [
    ("sst", "2011-10-02T00:00:00Z", "2011-10-04T00:00:00Z"),
    ("value_added", "2019-03-28T00:00:00Z", "2019-03-30T00:00:00Z"),
    ("quickscat", "2009-11-19T00:00:00Z", "2009-11-21T00:00:00Z"),
    ("oceansat2", "2020-04-29T00:00:00Z", "2020-05-01T00:00:00Z"),
    ("argo_vam", "2026-07-13T00:00:00Z", "2026-07-15T00:00:00Z"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Acquire a small INCOIS core-data batch")
    parser.add_argument("--min-lon", type=float, default=68.0)
    parser.add_argument("--max-lon", type=float, default=78.0)
    parser.add_argument("--min-lat", type=float, default=8.0)
    parser.add_argument("--max-lat", type=float, default=24.0)
    parser.add_argument("--min-depth", type=float, default=5.0)
    parser.add_argument("--max-depth", type=float, default=200.0)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "datasets" / "raw" / "incois")
    parser.add_argument("--continue-on-error", action="store_true")
    return parser.parse_args()


def run_download(args: argparse.Namespace, dataset: str, start: str, end: str) -> int:
    command = [
        sys.executable,
        str(DOWNLOADER),
        "--dataset", dataset,
        "--start", start,
        "--end", end,
        "--min-lon", str(args.min_lon),
        "--max-lon", str(args.max_lon),
        "--min-lat", str(args.min_lat),
        "--max-lat", str(args.max_lat),
        "--min-depth", str(args.min_depth),
        "--max-depth", str(args.max_depth),
        "--format", "parquet",
        "--output-dir", str(args.output_dir),
    ]
    print("\n$ " + " ".join(command))
    return subprocess.call(command, cwd=ROOT)


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    failures = 0
    for dataset, start, end in BATCHES:
        print(f"\n=== {dataset}: {start} -> {end} ===")
        code = run_download(args, dataset, start, end)
        if code != 0:
            failures += 1
            print(f"FAILED: {dataset} (exit code {code})")
            if not args.continue_on_error:
                raise SystemExit(code)
        else:
            print(f"OK: {dataset}")

    if failures:
        raise SystemExit(f"{failures} dataset batch(es) failed")
    print("\nAll configured INCOIS core batches completed.")


if __name__ == "__main__":
    main()
