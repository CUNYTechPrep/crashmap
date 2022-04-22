# Build the React front end.
FROM node:16-alpine as build-react
ENV PATH /app/node_modules/.bin:$PATH
WORKDIR /app/client
COPY client/package.json client/package-lock.json ./
RUN npm install
COPY ./client/src ./src
COPY ./client/public ./public
RUN npm run build

# Build the API with the client as static files.
FROM python:3.10
ARG APP_ENVIRONMENT
ARG APP_PORT
ENV FLASK_ENV=$APP_ENVIRONMENT
WORKDIR /app
COPY --from=build-react /app/client/build ./client/build
COPY ./api ./api
WORKDIR /app/api
RUN pip install -r requirements/production.txt
EXPOSE $APP_PORT
WORKDIR /app/api
CMD ["gunicorn", "-b", ":$APP_PORT", "main:flask_app"]
