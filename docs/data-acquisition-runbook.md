# OceanAI data acquisition runbook

This runbook is for acquiring real provider data. Do not commit downloaded NetCDF/CSV/Parquet files to Git; the repository ignores them under `datasets/raw` and `datasets/processed`.

## 1. INCOIS

List configured public datasets:

```bash
python scripts/python/download_incois_erddap.py --list
```

Acquire the documented small Indian-west-coast smoke batch:

```bash
python scripts/python/acquire_incois_core.py
```

Validate the normalized outputs:

```bash
python scripts/python/validate_ocean_observations.py datasets/raw/incois/*.parquet
```

Build a manifest:

```bash
python scripts/python/build_data_manifest.py datasets/raw/incois --output datasets/raw/incois/manifest.json
```

## 2. Copernicus Marine

Configure the account through environment variables or the Copernicus Marine Toolbox credential store. Never place credentials in the repository.

```bash
export COPERNICUSMARINE_SERVICE_USERNAME="..."
export COPERNICUSMARINE_SERVICE_PASSWORD="..."
```

Check the downloader without making a network request:

```bash
python scripts/python/download_copernicus_subset.py --dataset waves --dry-run
python scripts/python/download_copernicus_subset.py --dataset currents --dry-run
```

Acquire a small regional forecast subset:

```bash
python scripts/python/download_copernicus_subset.py \
  --dataset waves \
  --start 2026-09-05T00:00:00 \
  --end 2026-09-06T00:00:00 \
  --min-lon 68 --max-lon 78 \
  --min-lat 8 --max-lat 24
```

## 3. PostgreSQL ingestion

After a real normalized Parquet/CSV file exists, set `DATABASE_URL` and run:

```bash
python scripts/python/ingest_ocean_parquet.py datasets/raw/incois/*.parquet --dry-run
python scripts/python/ingest_ocean_parquet.py datasets/raw/incois/*.parquet
```

The normalized table is `ocean_observations`. It is independent of application users and preserves source, dataset, timestamp, depth and quality metadata.

## 4. Verify database contents

```bash
DATABASE_URL="..." python scripts/python/report_ocean_data.py
```

For the schema migration:

```bash
cd backend
alembic upgrade head
```

## 5. ORCA verification

Once the database contains real rows, query a selected Indian-coast point and confirm that ORCA returns the normalized observations before relying on any risk/decision output. Missing provider values must remain missing; the system must not invent safety evidence.
