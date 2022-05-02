COPY boro FROM PROGRAM 'xzcat /docker-entrypoint-initdb.d/boro.csv.xz' CSV HEADER;
COPY nta2020 FROM PROGRAM 'xzcat /docker-entrypoint-initdb.d/nta2020.csv.xz' CSV HEADER;
COPY h3 FROM PROGRAM 'xzcat /docker-entrypoint-initdb.d/h3.csv.xz' CSV HEADER;
COPY h3_nta2020 FROM PROGRAM 'xzcat /docker-entrypoint-initdb.d/h3_nta2020.csv.xz' CSV HEADER;
--COPY collision FROM '/docker-entrypoint-initdb.d/collision.csv' CSV HEADER;
--COPY vehicle FROM '/docker-entrypoint-initdb.d/vehicle.csv' CSV HEADER;
--COPY person FROM '/docker-entrypoint-initdb.d/person.csv' CSV HEADER;
