-- Enable PostGIS.
--CREATE EXTENSION postgis;

-- Enable PostGIS raster support.
--CREATE EXTENSION postgis_raster;

-- Enable PostGIS topology support.
--CREATE EXTENSION postgis_topology;

-- Create tables.
CREATE TABLE IF NOT EXISTS boro (
    id INTEGER NOT NULL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    geometry geometry NOT NULL CHECK (geometrytype(geometry) = ANY (ARRAY['MULTIPOLYGON'::text, 'POLYGON'::text])),
    land_geometry geometry NOT NULL CHECK (geometrytype(land_geometry) = ANY (ARRAY['MULTIPOLYGON'::text, 'POLYGON'::text]))--,
    --CONSTRAINT ck_boro_geometry_covers_land_geometry CHECK (st_covers(geometry, land_geometry))
);

CREATE TABLE IF NOT EXISTS nta2020 (
    id VARCHAR(6) NOT NULL PRIMARY KEY CHECK (id ~ '^(BK|BX|MN|QN|SI)(\d{4})?$'),
    name VARCHAR UNIQUE,
    boro_id INTEGER NOT NULL,
    geometry geometry NOT NULL CHECK (geometrytype(geometry) = ANY (ARRAY['MULTIPOLYGON'::text, 'POLYGON'::text])),
    CONSTRAINT fk_nta2020_boro_id FOREIGN KEY (boro_id) REFERENCES boro(id)
);

CREATE TABLE IF NOT EXISTS h3 (
    h3_index BIGINT NOT NULL PRIMARY KEY,
    only_water BOOLEAN NOT NULL,
    geometry geometry(polygon) NOT NULL
);

CREATE TABLE IF NOT EXISTS h3_nta2020 (
    h3_index BIGINT NOT NULL,
    nta2020_id VARCHAR(6) NOT NULL,
    PRIMARY KEY (h3_index, nta2020_id),
    CONSTRAINT fk_h3_nta2020_h3_index FOREIGN KEY (h3_index) REFERENCES h3(h3_index),
    CONSTRAINT fk_h3_nta2020_nta2020_id FOREIGN KEY (nta2020_id) REFERENCES nta2020(id)
);

CREATE TABLE IF NOT EXISTS collision (
    id BIGINT NOT NULL PRIMARY KEY,
    date DATE NOT NULL,
    time TIME(0) NOT NULL,
    latitude REAL,
    longitude REAL,
    h3_index BIGINT,
    nta2020_id VARCHAR(6),
    CONSTRAINT fk_collision_h3_index FOREIGN KEY (h3_index) REFERENCES h3(h3_index),
    CONSTRAINT fk_collision_nta2020_id FOREIGN KEY (nta2020_id) REFERENCES nta2020(id)
);

CREATE TABLE IF NOT EXISTS vehicle (
    id BIGINT NOT NULL PRIMARY KEY,
    collision_id BIGINT NOT NULL,
    state_registration VARCHAR,
    type VARCHAR,
    make VARCHAR,
    model VARCHAR,
    year INTEGER,
    travel_direction VARCHAR,
    occupants INTEGER,
    driver_sex VARCHAR,
    driver_license_status VARCHAR,
    driver_license_jurisdiction VARCHAR,
    pre_crash VARCHAR,
    point_of_impact VARCHAR,
    damages VARCHAR ARRAY CHECK (array_length(damages, 1) BETWEEN 1 AND 4),
    public_property_damage VARCHAR,
    public_property_damage_type VARCHAR,
    contributing_factors VARCHAR ARRAY CHECK (array_length(contributing_factors, 1) IN (1, 2)),
    CONSTRAINT fk_vehicle_collision_id FOREIGN KEY (collision_id) REFERENCES collision(id)
);

CREATE TABLE IF NOT EXISTS person (
    id BIGINT NOT NULL PRIMARY KEY,
    collision_id BIGINT NOT NULL,
    vehicle_id BIGINT,
    dangling_vehicle_id BIGINT,
    type VARCHAR,
    injury VARCHAR,
    age INTEGER,
    ejection VARCHAR,
    emotional_status VARCHAR,
    bodily_injury VARCHAR,
    position_in_vehicle VARCHAR,
    safety_equipment VARCHAR,
    location VARCHAR,
    action VARCHAR,
    complaint VARCHAR,
    role VARCHAR,
    contributing_factors VARCHAR ARRAY CHECK (array_length(contributing_factors, 1) IN (1, 2)),
    sex VARCHAR,
    CONSTRAINT fk_person_collision_id FOREIGN KEY (collision_id) REFERENCES collision(id),
    CONSTRAINT fk_person_vehicle_id FOREIGN KEY (vehicle_id) REFERENCES vehicle(id),
    CONSTRAINT ck_vehicle_id_and_dangling_vehicle_id_are_mutually_exclusive
        CHECK (NOT (vehicle_id IS NOT NULL AND dangling_vehicle_id IS NOT NULL))
);

-- Create indices.
--CREATE INDEX idx_boro_geometry ON boro USING gist (geometry);

CREATE INDEX idx_nta2020_geometry ON nta2020 USING gist (geometry);

CREATE INDEX idx_h3_cell_geometry ON h3 USING gist (geometry);

CREATE INDEX idx_collision_date ON collision USING btree (date);
--CREATE INDEX idx_collision_time ON collision USING btree (time);
CREATE INDEX idx_collision_h3_index ON collision USING btree (h3_index);
CREATE INDEX idx_collision_nta2020_id ON collision USING btree (nta2020_id);

-- Create triggers.
CREATE FUNCTION compute_h3_index_and_nta2020_id_from_location()
    RETURNS trigger AS
$$
DECLARE
    location geometry(point);
BEGIN
    IF new.latitude IS NULL OR new.longitude IS NULL THEN
        new.latitude := NULL;
        new.longitude := NULL;
        new.h3_index := NULL;
        new.nta2020_id := NULL;
    ELSE
        location := st_point(new.longitude, new.latitude);
        new.h3_index := (SELECT h3.h3_index
                         FROM h3
                         ORDER BY h3.geometry <-> location
                         LIMIT 1);
        new.nta2020_id := (SELECT nta2020.id
                           FROM nta2020
                           ORDER BY nta2020.geometry <-> location
                           LIMIT 1);
    END IF;
    RETURN new;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER collision_insert
    BEFORE INSERT
    ON collision
    FOR EACH ROW
    EXECUTE PROCEDURE compute_h3_index_and_nta2020_id_from_location();

CREATE TRIGGER collision_update
    BEFORE UPDATE
    ON collision
    FOR EACH ROW
    WHEN (old.latitude IS DISTINCT FROM new.latitude OR
          old.longitude IS DISTINCT FROM new.longitude OR
          old.h3_index IS DISTINCT FROM new.h3_index OR
          old.nta2020_id IS DISTINCT FROM new.nta2020_id)
    EXECUTE PROCEDURE compute_h3_index_and_nta2020_id_from_location();
