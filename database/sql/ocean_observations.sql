-- Normalized storage for downloaded/provider-supplied ocean observations.
-- Raw NetCDF/CSV/Parquet files remain outside Git for reproducibility and size.

CREATE TABLE IF NOT EXISTS ocean_observations (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    depth_m DOUBLE PRECISION,
    variable VARCHAR(64) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(32),
    source VARCHAR(64) NOT NULL,
    dataset VARCHAR(160) NOT NULL,
    data_type VARCHAR(32) NOT NULL,
    quality_flag VARCHAR(32) NOT NULL DEFAULT 'present',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (timestamp, latitude, longitude, depth_m, variable, source, dataset)
);

CREATE INDEX IF NOT EXISTS idx_ocean_observations_time
    ON ocean_observations (timestamp);

CREATE INDEX IF NOT EXISTS idx_ocean_observations_location
    ON ocean_observations (latitude, longitude);

CREATE INDEX IF NOT EXISTS idx_ocean_observations_variable_time
    ON ocean_observations (variable, timestamp);

CREATE INDEX IF NOT EXISTS idx_ocean_observations_depth
    ON ocean_observations (depth_m);
