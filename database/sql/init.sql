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

-- Create views.
CREATE VIEW h3_summary AS
    SELECT collision.h3_index,
           collision.date,
           count(DISTINCT collision.id) AS collisions,
           count(DISTINCT vehicle.id) AS vehicles,
           count(DISTINCT person.id) AS people,
           count(DISTINCT person.id) FILTER (WHERE person.type = 'Occupant') AS occupants,
           count(DISTINCT person.id) FILTER (WHERE person.type = 'Bicyclist') AS cyclists,
           count(DISTINCT person.id) FILTER (WHERE person.type = 'Pedestrian') AS pedestrians,
           count(DISTINCT person.id) FILTER (WHERE person.type = 'Other Motorized') AS other_people,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Injured') AS people_injured,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Injured' AND person.type = 'Occupant') AS occupants_injured,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Injured' AND person.type = 'Bicyclist') AS cyclists_injured,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Injured' AND person.type = 'Pedestrian') AS pedestrians_injured,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Injured' AND person.type = 'Other Motorized') AS other_people_injured,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Killed') AS people_killed,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Killed' AND person.type = 'Occupant') AS occupants_killed,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Killed' AND person.type = 'Bicyclist') AS cyclists_killed,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Killed' AND person.type = 'Pedestrian') AS pedestrians_killed,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Killed' AND person.type = 'Other Motorized') AS other_people_killed
    FROM collision
    LEFT JOIN vehicle ON collision.id = vehicle.collision_id
    LEFT JOIN person ON collision.id = person.collision_id
    GROUP BY collision.h3_index, collision.date
    ORDER BY collision.h3_index, collision.date;

CREATE VIEW nta2020_summary AS
    SELECT collision.nta2020_id,
           collision.date,
           count(DISTINCT collision.id) AS collisions,
           count(DISTINCT vehicle.id) AS vehicles,
           count(DISTINCT person.id) AS people,
           count(DISTINCT person.id) FILTER (WHERE person.type = 'Occupant') AS occupants,
           count(DISTINCT person.id) FILTER (WHERE person.type = 'Bicyclist') AS cyclists,
           count(DISTINCT person.id) FILTER (WHERE person.type = 'Pedestrian') AS pedestrians,
           count(DISTINCT person.id) FILTER (WHERE person.type = 'Other Motorized') AS other_people,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Injured') AS people_injured,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Injured' AND person.type = 'Occupant') AS occupants_injured,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Injured' AND person.type = 'Bicyclist') AS cyclists_injured,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Injured' AND person.type = 'Pedestrian') AS pedestrians_injured,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Injured' AND person.type = 'Other Motorized') AS other_people_injured,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Killed') AS people_killed,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Killed' AND person.type = 'Occupant') AS occupants_killed,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Killed' AND person.type = 'Bicyclist') AS cyclists_killed,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Killed' AND person.type = 'Pedestrian') AS pedestrians_killed,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Killed' AND person.type = 'Other Motorized') AS other_people_killed
    FROM collision
    LEFT JOIN vehicle ON collision.id = vehicle.collision_id
    LEFT JOIN person ON collision.id = person.collision_id
    GROUP BY collision.nta2020_id, collision.date
    ORDER BY collision.nta2020_id, collision.date;

CREATE VIEW boro_summary AS
    SELECT nta2020.boro_id,
           collision.date,
           count(DISTINCT collision.id) AS collisions,
           count(DISTINCT vehicle.id) AS vehicles,
           count(DISTINCT person.id) AS people,
           count(DISTINCT person.id) FILTER (WHERE person.type = 'Occupant') AS occupants,
           count(DISTINCT person.id) FILTER (WHERE person.type = 'Bicyclist') AS cyclists,
           count(DISTINCT person.id) FILTER (WHERE person.type = 'Pedestrian') AS pedestrians,
           count(DISTINCT person.id) FILTER (WHERE person.type = 'Other Motorized') AS other_people,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Injured') AS people_injured,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Injured' AND person.type = 'Occupant') AS occupants_injured,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Injured' AND person.type = 'Bicyclist') AS cyclists_injured,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Injured' AND person.type = 'Pedestrian') AS pedestrians_injured,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Injured' AND person.type = 'Other Motorized') AS other_people_injured,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Killed') AS people_killed,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Killed' AND person.type = 'Occupant') AS occupants_killed,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Killed' AND person.type = 'Bicyclist') AS cyclists_killed,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Killed' AND person.type = 'Pedestrian') AS pedestrians_killed,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Killed' AND person.type = 'Other Motorized') AS other_people_killed
    FROM nta2020
    INNER JOIN collision ON nta2020.id = collision.nta2020_id
    LEFT JOIN vehicle ON collision.id = vehicle.collision_id
    LEFT JOIN person ON collision.id = person.collision_id
    GROUP BY nta2020.boro_id, collision.date
    ORDER BY nta2020.boro_id, collision.date;

CREATE VIEW city_summary AS
    SELECT collision.date,
           count(DISTINCT collision.id) AS collisions,
           count(DISTINCT vehicle.id) AS vehicles,
           count(DISTINCT person.id) AS people,
           count(DISTINCT person.id) FILTER (WHERE person.type = 'Occupant') AS occupants,
           count(DISTINCT person.id) FILTER (WHERE person.type = 'Bicyclist') AS cyclists,
           count(DISTINCT person.id) FILTER (WHERE person.type = 'Pedestrian') AS pedestrians,
           count(DISTINCT person.id) FILTER (WHERE person.type = 'Other Motorized') AS other_people,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Injured') AS people_injured,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Injured' AND person.type = 'Occupant') AS occupants_injured,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Injured' AND person.type = 'Bicyclist') AS cyclists_injured,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Injured' AND person.type = 'Pedestrian') AS pedestrians_injured,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Injured' AND person.type = 'Other Motorized') AS other_people_injured,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Killed') AS people_killed,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Killed' AND person.type = 'Occupant') AS occupants_killed,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Killed' AND person.type = 'Bicyclist') AS cyclists_killed,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Killed' AND person.type = 'Pedestrian') AS pedestrians_killed,
           count(DISTINCT person.id) FILTER (WHERE person.injury = 'Killed' AND person.type = 'Other Motorized') AS other_people_killed
    FROM collision
    LEFT JOIN vehicle ON collision.id = vehicle.collision_id
    LEFT JOIN person ON collision.id = person.collision_id
    GROUP BY collision.date
    ORDER BY collision.date;

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
