FROM python:3.8

COPY . /app/

WORKDIR /app

RUN pip install poetry
RUN poetry install --with dev,docs -E all
ENV OPENAI_API_KEY=x

RUN poetry run pytest --fast-test-mode .