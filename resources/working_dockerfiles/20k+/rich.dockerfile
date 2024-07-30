FROM python:3.9-slim
WORKDIR /app
COPY . /app/
RUN pip install poetry
RUN poetry install
RUN poetry run pytest
