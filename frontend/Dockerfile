# build env
FROM node:13.12.0-alpine as build
WORKDIR /app
COPY ./frontend/package*.json /app
RUN npm install
COPY ./frontend /app
RUN npm run build
CMD cp -r build result_build
