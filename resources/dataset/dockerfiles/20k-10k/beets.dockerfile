FROM python:3.8

COPY . /app/

WORKDIR /app

RUN pip install poetry poethepoet

RUN poetry install

RUN poetry run pytest