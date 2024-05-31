# Use the official Python image as the base image
FROM python:3.9-slim

# Install git and other dependencies
RUN apt-get update && apt-get install -y git

# Set the working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/psf/black.git

# Move into the cloned repository
WORKDIR /app/black

# Set up the working environment for the repository
RUN python -m venv venv && . venv/bin/activate && pip install -e .[dev]

# Run the test suite
CMD pytest
