# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for 'make'
RUN apt-get update && apt-get install -y make

# Copy the entire repository into the container
COPY . /app/

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN make install-poetry && make dev

# Ensure pytest is installed
RUN pip install pytest

# Run the test suite
RUN pytest
