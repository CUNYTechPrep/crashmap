# Build the React front end.
FROM node:16-alpine as build-react
WORKDIR /app/client
ENV PATH /app/node_modules/.bin:$PATH
COPY client/package.json client/package-lock.json ./
COPY ./client/src ./src
COPY ./client/public ./public
RUN npm install
RUN npm run build

# Build the API with the client as static files.
FROM python:3.10
WORKDIR /app
COPY --from=build-react /app/client/build ./client/build

COPY ./api ./api
WORKDIR /app/api
RUN pip install -r requirements/production.txt
ENV FLASK_ENV production

ENV PORT 8080
EXPOSE $PORT/tcp
WORKDIR /app/api
CMD gunicorn -b :${PORT} main:flask_app
