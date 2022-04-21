COPY collision FROM '/docker-entrypoint-initdb.d/collision.csv' CSV HEADER;
COPY vehicle FROM '/docker-entrypoint-initdb.d/vehicle.csv' CSV HEADER;
COPY person FROM '/docker-entrypoint-initdb.d/person.csv' CSV HEADER;
