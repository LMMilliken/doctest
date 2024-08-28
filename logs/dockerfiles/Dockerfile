# Use the official Python base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the entire repository into the container
COPY . /app/

# Install necessary build dependencies (assumed to be in the repo)
# Note: Replace with specific dependencies if known
RUN pip install pytest

# Run the tests
RUN pytest
