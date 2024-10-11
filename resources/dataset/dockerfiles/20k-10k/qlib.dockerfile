FROM python:3.8

COPY . /app/

WORKDIR /app

RUN pip install -e ".[dev]"
RUN pip install cachetools
WORKDIR /app/tests

RUN python -m pytest . -m "not slow"