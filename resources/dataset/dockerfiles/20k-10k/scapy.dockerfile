FROM python:3.8

COPY . /app/

WORKDIR /app

RUN pip install tox

RUN ./test/run_tests