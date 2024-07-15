FROM python:3

WORKDIR /app
COPY . /app/

# Install curl
RUN apt-get update && apt-get install -y curl

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python -

# Set up project dependencies
RUN poetry config virtualenvs.create false
RUN poetry install

# Run the test suite
RUN pytest
