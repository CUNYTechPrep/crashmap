ARG DOCKER_NODE_TAG
ARG DOCKER_PYTHON_TAG

# Build the React front end.
FROM node:${DOCKER_NODE_TAG?-err} as build-react
ARG APP_ENVIRONMENT
ARG APP_PORT
ARG DATABASE_HOST
ARG DATABASE_PORT
ARG DATABASE_NAME
ARG DATABASE_USERNAME
ARG DATABASE_PASSWORD
ENV APP_ENVIRONMENT=${APP_ENVIRONMENT?-err}
ENV APP_PORT=${APP_PORT?-err}
ENV DATABASE_HOST=${DATABASE_HOST?-err}
ENV DATABASE_PORT=${DATABASE_PORT?-err}
ENV DATABASE_NAME=${DATABASE_NAME?-err}
ENV DATABASE_USERNAME=${DATABASE_USERNAME?-err}
ENV DATABASE_PASSWORD=${DATABASE_PASSWORD?-err}
ENV PATH /app/node_modules/.bin:$PATH
WORKDIR /app/client
COPY client/package.json client/package-lock.json ./
RUN npm install
COPY ./client/src ./src
COPY ./client/public ./public
RUN npm run build

# Build the API with the client as static files.
FROM python:${DOCKER_PYTHON_TAG?-err}
ARG APP_ENVIRONMENT
ARG APP_PORT
ARG DATABASE_HOST
ARG DATABASE_PORT
ARG DATABASE_NAME
ARG DATABASE_USERNAME
ARG DATABASE_PASSWORD
ENV FLASK_ENV=${APP_ENVIRONMENT?-err}
ENV APP_PORT=${APP_PORT?-err}
ENV DATABASE_HOST=${DATABASE_HOST?-err}
ENV DATABASE_PORT=${DATABASE_PORT?-err}
ENV DATABASE_NAME=${DATABASE_NAME?-err}
ENV DATABASE_USERNAME=${DATABASE_USERNAME?-err}
ENV DATABASE_PASSWORD=${DATABASE_PASSWORD?-err}
WORKDIR /app
COPY --from=build-react /app/client/build ./client/build
COPY ./api ./api
WORKDIR /app/api
RUN pip install -r requirements/production.txt
EXPOSE 80
WORKDIR /app/api
CMD gunicorn -b :80 main:flask_app
