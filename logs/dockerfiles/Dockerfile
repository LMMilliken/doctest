# Use the official Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the entire repository into the container
COPY . /app/

# Install Poetry
RUN pip install poetry

# Update the lock file to match the current pyproject.toml
RUN poetry lock

# Create an isolated environment and install dependencies
RUN poetry install

# Run the test suite to confirm everything works
RUN poetry run pytest --cov-report term-missing --cov=rich tests/ -vv
