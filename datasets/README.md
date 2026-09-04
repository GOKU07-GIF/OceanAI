# OceanAI Data Pipeline

This directory is the source-of-truth plan for OceanAI ocean data.

## Current state

The repository does **not** contain the full ocean datasets yet. `datasets/raw/` is only a storage location; an empty/sample file is not real ocean data.

The catalog in [`catalog.yaml`](./catalog.yaml) records the datasets we intend to retrieve and their status.

## What we are collecting

### P0 — first real ORCA data path

1. Sea-surface temperature (SST)
2. Significant wave height
3. Wave period and direction
4. Wind speed/direction
5. Surface currents
6. Salinity
7. Sea-surface height

### P1 — fishing/PFZ reasoning

8. Chlorophyll-a
9. INCOIS PFZ advisories
10. Landing centres and sectors
11. EEZ/bathymetry reference layers
12. INCOIS ROMS SST/MLD/D20/currents

### P2 — historical/model context

13. Copernicus physics reanalysis
14. Copernicus biogeochemistry hindcast
15. INCOIS climatology
16. NOAA observation datasets for independent cross-checks

## Download strategy

We will **subset the Indian Ocean/Indian coastal region**, rather than downloading global archives. For development, use a small area and short time range first; expand only after validation.

Default development bounding box:

```text
Longitude: 50°E to 90°E
Latitude:   0°N to 25°N
```

For Copernicus Marine, the recommended programmatic path is the Copernicus Marine Toolbox `subset` API/CLI. It supports selecting variables, spatial extent, time range and depth, and can write NetCDF/Zarr/CSV/Parquet where supported.

Copernicus credentials must be supplied through the local environment/configuration; **never commit credentials to GitHub**.

## Raw vs processed

```text
datasets/
├── raw/          # original/subset provider files; do not commit large files
├── processed/    # normalized files generated locally
└── catalog.yaml  # dataset inventory and status
```

Large NetCDF/Zarr files should live in local storage, object storage, or a data volume rather than normal Git history.

## Normalized record target

The eventual database/feature layer should preserve provenance. At minimum each observation/forecast value should map to:

```text
timestamp
latitude
longitude
variable
value
unit
source
dataset
quality_flag
data_kind       # observation / forecast / reanalysis / advisory
```

Do not replace missing data with guessed values. Missing provider evidence must remain explicitly missing so ORCA can return an insufficient-evidence decision when required.

## Validation checklist

For every downloaded dataset we will verify:

- file opens successfully
- expected variables exist
- latitude/longitude coordinates are present and sensible
- timestamps are parseable and inside the requested range
- units are recorded
- no unexpected all-null/all-fill variables
- value ranges are physically plausible
- source/dataset/provenance is retained
- a small Indian coastal point can be queried successfully

A dataset is only marked `validated` after these checks pass.

## First download batch

Start with a small, reproducible batch:

- Copernicus SST NRT
- Copernicus daily physics forecast: temperature, salinity, currents, sea level
- Copernicus 3-hourly wave forecast: wave height/period/direction
- Copernicus daily biogeochemistry forecast: chlorophyll

Then validate at 2–3 Indian coastal test locations before expanding the time window or adding historical data.

## Official sources

- INCOIS Data Holdings: https://incois.gov.in/site/dataholdings.jsp
- INCOIS Ocean State Forecast: https://www.incois.gov.in/oceanservices/osfforecast.jsp
- INCOIS PFZ Geoportal: https://incois.gov.in/geoportal/MFASPFZ/index.html
- Copernicus Marine data access: https://help.marine.copernicus.eu/en/articles/16733110-how-to-access-and-download-copernicus-marine-data
