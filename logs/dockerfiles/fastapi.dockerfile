# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir poetry pytest

# Clone the repository
RUN git clone https://github.com/tiangolo/fastapi.git

# Change working directory to the cloned repository
WORKDIR /app/fastapi

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the tests
RUN pytest
