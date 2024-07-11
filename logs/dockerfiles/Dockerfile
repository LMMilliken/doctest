# Use the official Python base image with Python 3.9
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install git
RUN apt-get update && apt-get install -y git \
    && rm -rf /var/lib/apt/lists/*

# Clone the spaCy repository
RUN git clone https://github.com/explosion/spaCy.git \
    && cd spaCy \
    && pip install --no-cache-dir -r requirements.txt

# Set the working directory to the cloned repo
WORKDIR /app/spaCy

# Install pytest to run tests
RUN pip install pytest

# Run the test suite
RUN pytest