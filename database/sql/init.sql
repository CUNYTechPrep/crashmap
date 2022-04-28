-- Enable PostGIS.
--CREATE EXTENSION postgis;

-- Enable PostGIS raster support.
--CREATE EXTENSION postgis_raster;

-- Enable PostGIS topology support.
--CREATE EXTENSION postgis_topology;

-- Create tables.
CREATE TABLE IF NOT EXISTS boro (
    the_geom geometry(multipolygon) NOT NULL,
    boro_code INTEGER NOT NULL PRIMARY KEY,
    boro_name VARCHAR NOT NULL UNIQUE,
    shape_leng REAL NOT NULL,
    shape_area REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS nta (
    the_geom geometry NOT NULL CHECK (geometrytype(the_geom) = ANY (ARRAY['MULTIPOLYGON'::text, 'POLYGON'::text])),
    borocode INTEGER NOT NULL,
    countyfips INTEGER NOT NULL,
    nta2020 VARCHAR(6) NOT NULL PRIMARY KEY,
    ntaname VARCHAR NOT NULL UNIQUE,
    ntaabbrev VARCHAR NOT NULL UNIQUE,
    ntatype INTEGER NOT NULL,
    cdta2020 VARCHAR(4) NOT NULL,
    cdtaname VARCHAR NOT NULL,
    shape_leng REAL NOT NULL,
    shape_area REAL NOT NULL,
    CONSTRAINT fk_nta_borocode FOREIGN KEY (borocode) REFERENCES boro(boro_code)
);

CREATE TABLE IF NOT EXISTS collision (
    collision_id BIGINT NOT NULL PRIMARY KEY,
    crash_date DATE NOT NULL,
    crash_time TIME(0) NOT NULL,
    latitude REAL,
    longitude REAL,
    location geometry(point) GENERATED ALWAYS AS (st_point(longitude, latitude)) STORED
);

CREATE TABLE IF NOT EXISTS vehicle
(
    unique_id BIGINT NOT NULL PRIMARY KEY,
    collision_id BIGINT NOT NULL,
    state_registration VARCHAR,
    vehicle_type VARCHAR,
    vehicle_make VARCHAR,
    vehicle_model VARCHAR,
    vehicle_year INTEGER,
    travel_direction VARCHAR,
    vehicle_occupants INTEGER,
    driver_sex VARCHAR,
    driver_license_status VARCHAR,
    driver_license_jurisdiction VARCHAR,
    pre_crash VARCHAR,
    point_of_impact VARCHAR,
    vehicle_damage VARCHAR,
    vehicle_damage_1 VARCHAR,
    vehicle_damage_2 VARCHAR,
    vehicle_damage_3 VARCHAR,
    public_property_damage VARCHAR,
    public_property_damage_type VARCHAR,
    contributing_factor_1 VARCHAR,
    contributing_factor_2 VARCHAR,
    CONSTRAINT fk_vehicle_collision_id FOREIGN KEY (collision_id) REFERENCES collision(collision_id)
);

CREATE TABLE IF NOT EXISTS person
(
    unique_id BIGINT NOT NULL PRIMARY KEY,
    collision_id BIGINT NOT NULL,
    person_type VARCHAR,
    person_injury VARCHAR,
    vehicle_id BIGINT,
    person_age INTEGER,
    ejection VARCHAR,
    emotional_status VARCHAR,
    bodily_injury VARCHAR,
    position_in_vehicle VARCHAR,
    safety_equipment VARCHAR,
    ped_location VARCHAR,
    ped_action VARCHAR,
    complaint VARCHAR,
    ped_role VARCHAR,
    contributing_factor_1 VARCHAR,
    contributing_factor_2 VARCHAR,
    person_sex VARCHAR,
    CONSTRAINT fk_person_collision_id FOREIGN KEY (collision_id) REFERENCES collision(collision_id)--,
    --CONSTRAINT fk_person_vehicle_id FOREIGN KEY (vehicle_id) REFERENCES vehicle(unique_id)
);

-- Create views.


-- Create indices.
CREATE INDEX idx_boro_the_geom ON boro USING gist (the_geom);
CREATE INDEX idx_nta_the_geom ON nta USING gist (the_geom);

CREATE INDEX idx_collision_crash_date ON collision USING btree (crash_date);
CREATE INDEX idx_collision_crash_time ON collision USING btree (crash_time);
CREATE INDEX idx_collision_location ON collision USING gist (location);
