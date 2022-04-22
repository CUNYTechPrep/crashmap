# Initialize the database.
FROM postgis/postgis:14-master as initializer
ARG DATABASE_USERNAME
ARG DATABASE_PASSWORD
ARG DATABASE_NAME
ENV POSTGRES_USER=$DATABASE_USERNAME
ENV POSTGRES_PASSWORD=$DATABASE_PASSWORD
ENV POSTGRES_DB=$DATABASE_NAME
ENV PGDATA /data
COPY /sql /docker-entrypoint-initdb.d
WORKDIR /docker-entrypoint-initdb.d
RUN ["apt", "update"]
RUN ["apt", "install", "zpaq"]
RUN ["zpaq", "x", "data.zpaq"]
RUN ["sed", "-i", "s/exec \"$@\"/echo \"Skipping...\"/", "/usr/local/bin/docker-entrypoint.sh"]
RUN ["/usr/local/bin/docker-entrypoint.sh", "postgres"]

# Copy the data without the SQL sources.
FROM postgis/postgis:14-master
ARG DATABASE_PORT
COPY --from=initializer /data $PGDATA
