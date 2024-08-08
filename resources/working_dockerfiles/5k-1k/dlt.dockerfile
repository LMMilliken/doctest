FROM python:3.11
WORKDIR /app
COPY . /app/
RUN pip install poetry
RUN poetry install --no-interaction --with sentry-sdk

#only testing a subset as the dependencies vary a lot between test targets
RUN poetry run pytest tests/common
