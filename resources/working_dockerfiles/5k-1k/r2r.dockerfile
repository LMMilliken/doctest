FROM python:3.11
WORKDIR /app
COPY . /app/
RUN pip install poetry
WORKDIR /app/py
RUN poetry install -E core
RUN poetry run pytest
