FROM python:3.8

COPY . /app/

WORKDIR /app

RUN scripts/install

RUN scripts/test