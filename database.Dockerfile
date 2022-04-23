ARG DOCKER_POSTGIS_TAG

# Initialize the database.
FROM postgis/postgis:${DOCKER_POSTGIS_TAG?-err} as initializer
ARG DATABASE_USERNAME
ARG DATABASE_PASSWORD
ARG DATABASE_NAME
ENV POSTGRES_USER=${DATABASE_USERNAME?-err}
ENV POSTGRES_PASSWORD=${DATABASE_PASSWORD?-err}
ENV POSTGRES_DB=${DATABASE_NAME?-err}
ENV PGDATA /data
COPY /database/sql /docker-entrypoint-initdb.d
WORKDIR /docker-entrypoint-initdb.d
RUN ["apt", "update"]
RUN ["apt", "install", "zpaq"]
RUN ["zpaq", "x", "data.zpaq"]
RUN ["sed", "-i", "s/exec \"$@\"/echo \"Skipping...\"/", "/usr/local/bin/docker-entrypoint.sh"]
RUN ["/usr/local/bin/docker-entrypoint.sh", "postgres"]

# Copy the data without the SQL sources.
FROM postgis/postgis:${DOCKER_POSTGIS_TAG?-err}
ARG DATABASE_PORT
ARG DATABASE_USERNAME
ARG DATABASE_PASSWORD
ARG DATABASE_NAME
ENV POSTGRES_USER=${DATABASE_USERNAME?-err}
ENV POSTGRES_PASSWORD=${DATABASE_PASSWORD?-err}
ENV POSTGRES_DB=${DATABASE_NAME?-err}
COPY --from=initializer /data $PGDATA
