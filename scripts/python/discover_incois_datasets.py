"""Discover currently active public INCOIS ERDDAP datasets.

This avoids hard-coding assumptions about which public datasets are currently
exposed. The output can be redirected to a versioned metadata snapshot.

Usage:
  python scripts/python/discover_incois_datasets.py
  python scripts/python/discover_incois_datasets.py --contains sst
"""

from __future__ import annotations

import argparse
from io import StringIO

import pandas as pd
import requests

ENDPOINT = "https://erddap.incois.gov.in/erddap/tabledap/allDatasets.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Discover public INCOIS ERDDAP datasets")
    parser.add_argument("--contains", help="Filter dataset ID/title/institution by substring")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    response = requests.get(ENDPOINT, timeout=60)
    response.raise_for_status()
    frame = pd.read_csv(StringIO(response.text))

    if args.contains:
        term = args.contains.casefold()
        mask = frame.astype(str).apply(
            lambda column: column.str.casefold().str.contains(term, na=False)
        ).any(axis=1)
        frame = frame.loc[mask]

    print(frame.to_string(index=False))
    print(f"\nDiscovered {len(frame)} public/visible INCOIS ERDDAP rows.")


if __name__ == "__main__":
    main()
