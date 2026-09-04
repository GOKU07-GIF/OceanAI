"""Download small, reproducible Copernicus Marine subsets for OceanAI.

Examples:
  python scripts/python/download_copernicus_subset.py --list
  python scripts/python/download_copernicus_subset.py --dataset sst --start 2026-09-01 --end 2026-09-03
  python scripts/python/download_copernicus_subset.py --dataset physics --start 2026-09-01 --end 2026-09-03
  python scripts/python/download_copernicus_subset.py --dataset waves --start 2026-09-01T00:00:00 --end 2026-09-03T21:00:00
  python scripts/python/download_copernicus_subset.py --dataset bgc --start 2026-09-01 --end 2026-09-03

The script intentionally downloads only a regional/time subset. It never stores
Copernicus credentials in the repository.
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
    "minimum_longitude": 50.0,
    "maximum_longitude": 90.0,
    "minimum_latitude": 0.0,
    "maximum_latitude": 25.0,
}

OUTPUT_DIR = Path("datasets/raw/copernicus")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download an OceanAI Copernicus subset")
    parser.add_argument("--dataset", choices=sorted(DATASETS), help="Dataset alias")
    parser.add_argument("--list", action="store_true", help="List configured datasets")
    parser.add_argument("--start", help="Start datetime, e.g. 2026-09-01T00:00:00")
    parser.add_argument("--end", help="End datetime, e.g. 2026-09-03T00:00:00")
    parser.add_argument("--min-lon", type=float, default=DEFAULT_BBOX["minimum_longitude"])
    parser.add_argument("--max-lon", type=float, default=DEFAULT_BBOX["maximum_longitude"])
    parser.add_argument("--min-lat", type=float, default=DEFAULT_BBOX["minimum_latitude"])
    parser.add_argument("--max-lat", type=float, default=DEFAULT_BBOX["maximum_latitude"])
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.list:
        for alias, config in DATASETS.items():
            print(f"{alias}: {config['dataset_id']} -> {', '.join(config['variables'])}")
        return

    if not args.dataset or not args.start or not args.end:
        raise SystemExit("--dataset, --start and --end are required (or use --list)")

    config = DATASETS[args.dataset]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{args.dataset}_{args.start.replace(':', '').replace('-', '')}_{args.end.replace(':', '').replace('-', '')}.nc"

    print("Downloading Copernicus subset:")
    print(f"  dataset : {config['dataset_id']}")
    print(f"  variables: {', '.join(config['variables'])}")
    print(f"  bbox    : {args.min_lon},{args.max_lon},{args.min_lat},{args.max_lat}")
    print(f"  time    : {args.start} -> {args.end}")
    print(f"  output  : {args.output_dir / filename}")

    copernicusmarine.subset(
        dataset_id=config["dataset_id"],
        variables=config["variables"],
        minimum_longitude=args.min_lon,
        maximum_longitude=args.max_lon,
        minimum_latitude=args.min_lat,
        maximum_latitude=args.max_lat,
        start_datetime=args.start,
        end_datetime=args.end,
        output_directory=str(args.output_dir),
        output_filename=filename,
        netcdf_compression_level=4,
    )

    print(f"Downloaded: {args.output_dir / filename}")
    print("Next step: run the dataset validation checks before marking it validated in catalog.yaml.")


if __name__ == "__main__":
    main()
