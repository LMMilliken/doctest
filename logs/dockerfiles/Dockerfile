# Use a Python base image
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the entire repository into the container
COPY . .

# Install Poetry
RUN pip install poetry

# Install the dependencies using Poetry
RUN poetry install --all-extras

# Build the project (install editable mode)
RUN poetry build && pip install --no-build-isolation --editable .

# Run the test suite
RUN poetry run pytest
