FROM python:3.8

WORKDIR /app

COPY . /app/

RUN pip install poetry

RUN poetry install --all-extras

RUN poetry run pytest