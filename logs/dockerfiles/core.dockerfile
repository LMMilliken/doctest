# Dockerfile to clone the Home Assistant core repository, set up the environment, and run tests

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install any needed packages specified in requirements.txt
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository
RUN git clone https://github.com/home-assistant/core.git

# Set working directory
WORKDIR /core

# Install the dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Ensure pytest is installed (in case it is not included in dependencies)
RUN pip install pytest

# Run tests to verify that installation succeeds
RUN pytest
