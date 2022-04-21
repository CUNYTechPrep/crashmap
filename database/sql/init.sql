-- Enable PostGIS.
CREATE EXTENSION postgis;

-- Enable raster support.
CREATE EXTENSION postgis_raster;

-- Enable Topology.
CREATE EXTENSION postgis_topology;

-- Create tables.
CREATE TABLE IF NOT EXISTS collision (
    collision_id BIGINT NOT NULL,
    crash_date DATE NOT NULL,
    crash_time TIME(0) NOT NULL,
    latitude REAL,
    longitude REAL,
    location geography(POINT) GENERATED ALWAYS AS (ST_POINT(latitude, longitude)) STORED,
    PRIMARY KEY (collision_id)
);
