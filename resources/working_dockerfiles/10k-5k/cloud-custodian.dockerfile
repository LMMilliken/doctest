FROM python:3.8

WORKDIR /app

COPY . /app/

RUN pip install poetry

RUN poetry install

RUN poetry run make install

RUN poetry run make test