"""Parse INCOIS PFZ advisory text into a normalized table.

INCOIS publishes PFZ advisories in text form with location (latitude/longitude),
depth and distance/direction from identifiable coastal landmarks. The exact
provider download endpoint is intentionally not hard-coded here because the
public PFZ service does not document a stable machine-readable endpoint.

Usage:
  python scripts/python/parse_pfz_text.py --input path/to/pfz_goa.txt --output datasets/processed/pfz_goa.csv --sector Goa

The parser is deliberately conservative. It extracts records only when both
latitude and longitude can be identified and preserves the original line for
manual audit.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

LAT_LON_RE = re.compile(
    r"(?P<lat>\d{1,2}(?:\.\d+)?)\s*[°:]?\s*(?:N|North)?\s*[,;/ ]+"
    r"(?P<lon>\d{2,3}(?:\.\d+)?)\s*[°:]?\s*(?:E|East)?",
    re.IGNORECASE,
)
DEPTH_RE = re.compile(r"(?:depth|depth of)\s*[:=-]?\s*(?P<depth>\d+(?:\.\d+)?)\s*(?:m|metre|meters?)?", re.IGNORECASE)
DISTANCE_RE = re.compile(r"(?P<distance>\d+(?:\.\d+)?)\s*(?:km|kms|nautical miles?|nm|miles?)", re.IGNORECASE)
DIRECTION_RE = re.compile(r"\b(N|NE|E|SE|S|SW|W|NW|North|North[- ]?East|East|South[- ]?East|South|South[- ]?West|West|North[- ]?West)\b", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Parse an INCOIS PFZ advisory text file")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sector", default="")
    parser.add_argument("--language", default="")
    return parser.parse_args()


def parse_line(line: str, source_line: int, sector: str, language: str) -> dict | None:
    match = LAT_LON_RE.search(line)
    if not match:
        return None

    depth_match = DEPTH_RE.search(line)
    distance_match = DISTANCE_RE.search(line)
    direction_match = DIRECTION_RE.search(line)

    return {
        "advisory_date": None,
        "sector": sector,
        "language": language,
        "latitude": float(match.group("lat")),
        "longitude": float(match.group("lon")),
        "depth_m": float(depth_match.group("depth")) if depth_match else None,
        "distance_value": float(distance_match.group("distance")) if distance_match else None,
        "distance_unit": distance_match.group(0).split()[-1] if distance_match else None,
        "direction": direction_match.group(0) if direction_match else None,
        "source_line": source_line,
        "raw_text": line.strip(),
        "source": "INCOIS",
        "data_type": "pfz_advisory",
        "quality_flag": "present",
    }


def parse_file(path: Path, sector: str, language: str) -> pd.DataFrame:
    text = path.read_text(encoding="utf-8", errors="replace")
    records = []
    for number, line in enumerate(text.splitlines(), start=1):
        record = parse_line(line, number, sector, language)
        if record:
            records.append(record)

    if not records:
        raise ValueError(
            "No PFZ records with recognizable latitude/longitude were found. "
            "Keep the original file and review its format before changing the parser."
        )

    frame = pd.DataFrame(records)
    frame["source_file"] = path.name
    return frame


def main() -> None:
    args = parse_args()
    frame = parse_file(args.input, args.sector, args.language)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.suffix.lower() == ".csv":
        frame.to_csv(args.output, index=False)
    elif args.output.suffix.lower() == ".parquet":
        frame.to_parquet(args.output, index=False)
    else:
        raise SystemExit("Output must end with .csv or .parquet")
    print(f"Parsed {len(frame)} PFZ advisory records -> {args.output}")


if __name__ == "__main__":
    main()
