# Use the official Python image as base
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the entire repository into the container
COPY . /app/

# Install Poetry
RUN pip install poetry

# Installing project dependencies
RUN poetry install --all-extras

# Run the test suite
RUN poetry run pytest