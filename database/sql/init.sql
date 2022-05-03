-- Enable PostGIS.
--CREATE EXTENSION postgis;

-- Enable PostGIS raster support.
--CREATE EXTENSION postgis_raster;

-- Enable PostGIS topology support.
--CREATE EXTENSION postgis_topology;

-- Create types.
CREATE TYPE cardinal_direction AS ENUM (
    'North', 'East', 'South', 'West',
    'Northeast', 'Southeast',
    'Northwest', 'Southwest'
);

CREATE TYPE person_sex AS ENUM ('Female', 'Male');

CREATE TYPE person_type AS ENUM ('Bicyclist', 'Occupant', 'Pedestrian', 'Other Motorized');

CREATE TYPE injury_type AS ENUM ('Injured', 'Killed');

CREATE TYPE us_state AS ENUM (
    'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD',
    'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH',
    'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY'
);

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
    location geometry(point) NOT NULL,
    h3_index BIGINT NOT NULL,
    nta2020_id VARCHAR(6) NOT NULL,
    CONSTRAINT fk_collision_h3_index FOREIGN KEY (h3_index) REFERENCES h3(h3_index),
    CONSTRAINT fk_collision_nta2020_id FOREIGN KEY (nta2020_id) REFERENCES nta2020(id)
);

CREATE TABLE IF NOT EXISTS vehicle (
    id BIGINT NOT NULL PRIMARY KEY,
    collision_id BIGINT NOT NULL,
    state_registration us_state,
    type VARCHAR,
    make VARCHAR,
    model VARCHAR,
    year INTEGER,
    travel_direction cardinal_direction,
    occupants INTEGER,
    driver_sex VARCHAR,
    driver_license_status VARCHAR,
    driver_license_jurisdiction us_state,
    pre_crash VARCHAR,
    point_of_impact VARCHAR,
    damages VARCHAR ARRAY[4],
    public_property_damage BOOLEAN,
    public_property_damage_type VARCHAR,
    contributing_factors VARCHAR ARRAY[2],
    CONSTRAINT fk_vehicle_collision_id FOREIGN KEY (collision_id) REFERENCES collision(id)
);

CREATE TABLE IF NOT EXISTS person (
    id BIGINT NOT NULL PRIMARY KEY,
    collision_id BIGINT NOT NULL,
    vehicle_id BIGINT,
    type person_type,
    injury injury_type,
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
    contributing_factors VARCHAR ARRAY[2],
    sex person_sex,
    CONSTRAINT fk_person_collision_id FOREIGN KEY (collision_id) REFERENCES collision(id),
    CONSTRAINT fk_person_vehicle_id FOREIGN KEY (vehicle_id) REFERENCES vehicle(id)
);

CREATE TABLE IF NOT EXISTS h3_summary (
    h3_index BIGINT NOT NULL,
    date DATE NOT NULL,
    collisions BIGINT NOT NULL CHECK (collisions >= 0),
    vehicles BIGINT NOT NULL CHECK (vehicles >= 0),
    people BIGINT NOT NULL CHECK (people >= 0),
    occupants BIGINT NOT NULL CHECK (occupants >= 0),
    cyclists BIGINT NOT NULL CHECK (cyclists >= 0),
    pedestrians BIGINT NOT NULL CHECK (pedestrians >= 0),
    other_people BIGINT NOT NULL CHECK (other_people >= 0),
    people_injured BIGINT NOT NULL CHECK (people_injured >= 0),
    occupants_injured BIGINT NOT NULL CHECK (occupants_injured >= 0),
    cyclists_injured BIGINT NOT NULL CHECK (cyclists_injured >= 0),
    pedestrians_injured BIGINT NOT NULL CHECK (pedestrians_injured >= 0),
    other_people_injured BIGINT NOT NULL CHECK (other_people_injured >= 0),
    people_killed BIGINT NOT NULL CHECK (people_killed >= 0),
    occupants_killed BIGINT NOT NULL CHECK (occupants_killed >= 0),
    cyclists_killed BIGINT NOT NULL CHECK (cyclists_killed >= 0),
    pedestrians_killed BIGINT NOT NULL CHECK (pedestrians_killed >= 0),
    other_people_killed BIGINT NOT NULL CHECK (other_people_killed >= 0),
    PRIMARY KEY (h3_index, date),
    CONSTRAINT fk_h3_cell_summary_h3_index FOREIGN KEY (h3_index) REFERENCES h3(h3_index)
);

CREATE TABLE IF NOT EXISTS nta2020_summary (
    nta2020_id VARCHAR(6) NOT NULL,
    date DATE NOT NULL,
    collisions BIGINT NOT NULL CHECK (collisions >= 0),
    vehicles BIGINT NOT NULL CHECK (vehicles >= 0),
    people BIGINT NOT NULL CHECK (people >= 0),
    occupants BIGINT NOT NULL CHECK (occupants >= 0),
    cyclists BIGINT NOT NULL CHECK (cyclists >= 0),
    pedestrians BIGINT NOT NULL CHECK (pedestrians >= 0),
    other_people BIGINT NOT NULL CHECK (other_people >= 0),
    people_injured BIGINT NOT NULL CHECK (people_injured >= 0),
    occupants_injured BIGINT NOT NULL CHECK (occupants_injured >= 0),
    cyclists_injured BIGINT NOT NULL CHECK (cyclists_injured >= 0),
    pedestrians_injured BIGINT NOT NULL CHECK (pedestrians_injured >= 0),
    other_people_injured BIGINT NOT NULL CHECK (other_people_injured >= 0),
    people_killed BIGINT NOT NULL CHECK (people_killed >= 0),
    occupants_killed BIGINT NOT NULL CHECK (occupants_killed >= 0),
    cyclists_killed BIGINT NOT NULL CHECK (cyclists_killed >= 0),
    pedestrians_killed BIGINT NOT NULL CHECK (pedestrians_killed >= 0),
    other_people_killed BIGINT NOT NULL CHECK (other_people_killed >= 0),
    PRIMARY KEY (nta2020_id, date),
    CONSTRAINT fk_nta_summary_nta2020_id FOREIGN KEY (nta2020_id) REFERENCES nta2020(id)
);

-- Create views.
CREATE VIEW boro_summary AS
SELECT boro_id,
       date,
       sum(collisions) AS collisions,
       sum(vehicles) AS vehicles,
       sum(people) AS people,
       sum(occupants) AS occupants,
       sum(cyclists) AS cyclists,
       sum(pedestrians) AS pedestrians,
       sum(other_people) AS other_people,
       sum(people_injured) AS people_injured,
       sum(occupants_injured) AS occupants_injured,
       sum(cyclists_injured) AS cyclists_injured,
       sum(pedestrians_injured) AS pedestrians_injured,
       sum(other_people_injured) AS other_people_injured,
       sum(people_killed) AS people_killed,
       sum(occupants_killed) AS occupants_killed,
       sum(cyclists_killed) AS cyclists_killed,
       sum(pedestrians_killed) AS pedestrians_killed,
       sum(other_people_killed) AS other_people_killed
FROM nta2020_summary
JOIN nta2020 ON nta2020_summary.nta2020_id = nta2020.id
JOIN boro ON nta2020.boro_id = boro.id
GROUP BY boro_id, date
ORDER BY boro_id, date;

CREATE VIEW city_summary AS
SELECT date,
       sum(collisions) AS collisions,
       sum(vehicles) AS vehicles,
       sum(people) AS people,
       sum(occupants) AS occupants,
       sum(cyclists) AS cyclists,
       sum(pedestrians) AS pedestrians,
       sum(other_people) AS other_people,
       sum(people_injured) AS people_injured,
       sum(occupants_injured) AS occupants_injured,
       sum(cyclists_injured) AS cyclists_injured,
       sum(pedestrians_injured) AS pedestrians_injured,
       sum(other_people_injured) AS other_people_injured,
       sum(people_killed) AS people_killed,
       sum(occupants_killed) AS occupants_killed,
       sum(cyclists_killed) AS cyclists_killed,
       sum(pedestrians_killed) AS pedestrians_killed,
       sum(other_people_killed) AS other_people_killed
FROM nta2020_summary
GROUP BY date
ORDER BY date;

-- Create indices.
CREATE INDEX idx_boro_geometry ON boro USING gist (geometry);

CREATE INDEX idx_nta2020_geometry ON nta2020 USING gist (geometry);

CREATE INDEX idx_h3_cell_geometry ON h3 USING gist (geometry);

CREATE INDEX idx_collision_date ON collision USING btree (date);
CREATE INDEX idx_collision_time ON collision USING btree (time);
--CREATE INDEX idx_collision_location ON collision USING gist (location);
CREATE INDEX idx_collision_h3_index ON collision USING btree (h3_index);
CREATE INDEX idx_collision_nta2020_id ON collision USING btree (nta2020_id);
