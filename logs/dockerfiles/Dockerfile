# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Clone the spaCy repository
RUN git clone https://github.com/explosion/spaCy.git

# Move into the cloned repository directory
WORKDIR /usr/src/app/spaCy

# Copy the requirement file and install project dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install pytest (if not included in requirements.txt) to run tests
RUN pip install pytest

# Run tests to verify installation
RUN pytest
