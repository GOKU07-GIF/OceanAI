# INCOIS data acquisition plan

Verified against the INCOIS ERDDAP metadata pages on 2026-09-05.

## Public gridded datasets

| Dataset | ERDDAP ID | Variables | Role |
| --- | --- | --- | --- |
| Daily-OI-V2 SST | `NOAA_AVHRR_AMSR_datasets` | `sst`, `anom` | Historical SST/anomaly |
| Value Added Products | `incois_valueadded_products_datasets` | `MLD`, `ILD`, `D26`, `D20`, `HTCNT`, `DYN_HT`, `GEO_U`, `GEO_V` | Historical thermocline/mixed-layer/current context |
| QuickSCAT Daily | `incois_quickscat_daily_datasets` | `WIND_SPEED`, `ZONAL_WIND_SPEED`, `MERI_WIND_SPEED`, wind-stress fields | Historical wind |
| Oceansat-2 OCM | `incois_oceansat2_datasets` | `CHL`, `KD490`, `TSM` | Chlorophyll/productivity and water-quality context |
| IRS P4 OCM Chlorophyll | `IRS_chlorophyll_datasets` | `CHLOROPHYLL` | Historical chlorophyll |
| Indian ARGO | `Indian_ARGO_Floats` | provider-defined profile variables | Profile observations |
| INCOIS ARGO monthly VAM | `incois_argo_mnt_VAM` | `TEMP`, `SAL`, errors | Historical temperature/salinity profiles |
| INCOIS ARGO monthly McCreary | `incois_argo_mnt_McCreary` | profile variables | Historical profile/reanalysis context |

## Important coverage notes

The public ERDDAP datasets are not all current/forecast products. For example, the public Daily-OI SST dataset currently exposed by INCOIS ends at 2011-10-04, while the Value Added Products dataset covers 2004-01-10 through 2019-03-30. These are therefore valuable for historical features, anomaly baselines and model training, but they must not be presented as today's forecast.

QuickSCAT, Oceansat-2/OCM and ARGO products should be inspected for their actual time coverage before bulk ingestion. The `allDatasets` ERDDAP endpoint should be used as the source of truth for the current public dataset inventory.

## Download policy

1. Query a small Indian-region/time subset.
2. Save the source response as NetCDF when the gridded service supports it.
3. Validate coordinates, variables, time coverage, fill values and non-null counts.
4. Transform to the normalized long-form OceanAI observation schema.
5. Ingest into PostgreSQL through `scripts/python/ingest_ocean_table.py`.
6. Keep raw/processed data outside Git; only scripts, schemas and manifests belong in the repository.

## Normalized schema

```text
 timestamp
 latitude
 longitude
 variable
 value
 unit
 source
 dataset
 data_type
 quality_flag
```

## Source pages

- INCOIS ERDDAP dataset inventory: https://erddap.incois.gov.in/erddap/tabledap/allDatasets.html
- INCOIS SST: https://erddap.incois.gov.in/erddap/griddap/NOAA_AVHRR_AMSR_datasets.html
- INCOIS Value Added Products: https://erddap.incois.gov.in/erddap/griddap/incois_valueadded_products_datasets.html
- INCOIS QuickSCAT: https://erddap.incois.gov.in/erddap/griddap/incois_quickscat_daily_datasets.html
- INCOIS Oceansat-2 OCM: https://erddap.incois.gov.in/erddap/griddap/incois_oceansat2_datasets.html
- INCOIS IRS P4 OCM Chlorophyll: https://erddap.incois.gov.in/erddap/griddap/IRS_chlorophyll_datasets.html
