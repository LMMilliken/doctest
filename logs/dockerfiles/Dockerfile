# Use the official Python image from the Docker Hub
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry install

# Install Pytest for running tests
RUN poetry add pytest

# Run the test suite
RUN pytest