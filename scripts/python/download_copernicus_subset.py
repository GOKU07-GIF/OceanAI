"""Download small, reproducible Copernicus Marine subsets for OceanAI.

Credentials are resolved by the Copernicus Marine Toolbox from its configured
credentials file or the COPERNICUSMARINE_SERVICE_USERNAME and
COPERNICUSMARINE_SERVICE_PASSWORD environment variables.

Only regional/time subsets should be downloaded during development.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import copernicusmarine

DATASETS = {
    "sst": {
        "dataset_id": "cmems_obs-sst_glo_phy-temp_nrt_P1D-m",
        "variables": ["analysed_sst"],
    },
    "physics": {
        "dataset_id": "cmems_mod_glo_phy_anfc_0.083deg_P1D-m",
        "variables": ["thetao", "so", "uo", "vo", "zos"],
    },
    "currents": {
        "dataset_id": "cmems_mod_glo_phy-cur_anfc_0.083deg_PT6H-i",
        "variables": ["uo", "vo"],
    },
    "waves": {
        "dataset_id": "cmems_mod_glo_wav_anfc_0.083deg_PT3H-i",
        "variables": ["VHM0", "VTM02", "VMDR"],
    },
    "bgc": {
        "dataset_id": "cmems_mod_glo_bgc_anfc_0.25deg_P1D-m",
        "variables": ["chl"],
    },
}

DEFAULT_BBOX = {
    "minimum_longitude": 68.0,
    "maximum_longitude": 78.0,
    "minimum_latitude": 8.0,
    "maximum_latitude": 24.0,
}

OUTPUT_DIR = Path("datasets/raw/copernicus")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download an OceanAI Copernicus subset")
    parser.add_argument("--dataset", choices=sorted(DATASETS), help="Dataset alias")
    parser.add_argument("--list", action="store_true", help="List configured datasets")
    parser.add_argument("--start", help="Start datetime, e.g. 2026-09-05T00:00:00")
    parser.add_argument("--end", help="End datetime, e.g. 2026-09-06T00:00:00")
    parser.add_argument("--min-lon", type=float, default=DEFAULT_BBOX["minimum_longitude"])
    parser.add_argument("--max-lon", type=float, default=DEFAULT_BBOX["maximum_longitude"])
    parser.add_argument("--min-lat", type=float, default=DEFAULT_BBOX["minimum_latitude"])
    parser.add_argument("--max-lat", type=float, default=DEFAULT_BBOX["maximum_latitude"])
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--dry-run", action="store_true", help="Print the configured request without downloading")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.list:
        for alias, config in DATASETS.items():
            print(f"{alias}: {config['dataset_id']} -> {', '.join(config['variables'])}")
        return

    if not args.dataset:
        raise SystemExit("--dataset is required (or use --list)")
    if not args.dry_run and (not args.start or not args.end):
        raise SystemExit("--start and --end are required unless --dry-run is used")

    config = DATASETS[args.dataset]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    safe_start = (args.start or "request").replace(":", "").replace("-", "")
    safe_end = (args.end or "request").replace(":", "").replace("-", "")
    filename = f"{args.dataset}_{safe_start}_{safe_end}.nc"

    request = {
        "dataset_id": config["dataset_id"],
        "variables": config["variables"],
        "minimum_longitude": args.min_lon,
        "maximum_longitude": args.max_lon,
        "minimum_latitude": args.min_lat,
        "maximum_latitude": args.max_lat,
        "start_datetime": args.start,
        "end_datetime": args.end,
        "output_directory": str(args.output_dir),
        "output_filename": filename,
        "netcdf_compression_level": 4,
        "overwrite": False,
    }

    print("Copernicus subset request:")
    for key, value in request.items():
        print(f"  {key}: {value}")

    if args.dry_run:
        print("Dry run: no network request made.")
        return

    copernicusmarine.subset(**request)
    print(f"Downloaded: {args.output_dir / filename}")


if __name__ == "__main__":
    main()
