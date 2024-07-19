FROM python:3.8

WORKDIR /app

COPY . /app/

RUN pip install poetry

RUN poetry install

RUN poetry run pip install pytest

RUN poetry run pytest
