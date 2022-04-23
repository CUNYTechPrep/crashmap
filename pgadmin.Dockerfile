# Initialize the database.
FROM dpage/pgadmin4:6.8
ARG PGADMIN_USERNAME
ARG PGADMIN_PASSWORD
ARG DATABASE_HOST
ARG DATABASE_PORT
ARG DATABASE_NAME
ARG DATABASE_USERNAME
ENV PGADMIN_DEFAULT_EMAIL=${PGADMIN_USERNAME?-err}
ENV PGADMIN_DEFAULT_PASSWORD=${PGADMIN_PASSWORD?-err}
USER root
RUN echo {\"Servers\":{\"1\":{\"Name\":\"${DATABASE_NAME?-err}\",\"Group\":\"Servers\",\"Port\":${DATABASE_PORT?-err},\"Username\": \"${DATABASE_USERNAME?-err}\",\"Host\":\"${DATABASE_HOST?-err}\",\"SSLMode\":\"prefer\",\"MaintenanceDB\":\"${DATABASE_NAME?-err}\"}}} > /pgadmin4/servers.json
EXPOSE 80
