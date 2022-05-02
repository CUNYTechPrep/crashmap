ARG DOCKER_POSTGIS_TAG

# Initialize the database.
FROM postgis/postgis:${DOCKER_POSTGIS_TAG?-} as initializer
ARG DATABASE_PORT_DOCKER
ARG DATABASE_USERNAME
ARG DATABASE_PASSWORD
ARG DATABASE_NAME
ENV POSTGRES_USER=${DATABASE_USERNAME?-}
ENV POSTGRES_PASSWORD=${DATABASE_PASSWORD?-}
ENV POSTGRES_DB=${DATABASE_NAME?-}
ENV PGDATA /data
COPY database/sql /docker-entrypoint-initdb.d
WORKDIR /docker-entrypoint-initdb.d
RUN ["sed", "-i", "s/exec \"$@\"/echo \"Skipping...\"/", "/usr/local/bin/docker-entrypoint.sh"]
RUN ["/usr/local/bin/docker-entrypoint.sh", "postgres"]
RUN sed -i "s/#port = 5432/port = ${DATABASE_PORT_DOCKER?-}/" /data/postgresql.conf

# Copy the data without the SQL sources.
FROM postgis/postgis:${DOCKER_POSTGIS_TAG?-}
ARG DATABASE_PORT_DOCKER
ARG DATABASE_USERNAME
ARG DATABASE_PASSWORD
ARG DATABASE_NAME
ENV POSTGRES_USER=${DATABASE_USERNAME?-}
ENV POSTGRES_PASSWORD=${DATABASE_PASSWORD?-}
ENV POSTGRES_DB=${DATABASE_NAME?-}
COPY --from=initializer /data $PGDATA
EXPOSE ${DATABASE_PORT_DOCKER?-}
