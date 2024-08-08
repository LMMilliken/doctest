# Use a lightweight Python base image
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Install git as it might be required for some dependencies
RUN apt-get update && apt-get install -y git && apt-get clean

# Copy the entire repository into the container
COPY . /app/

# Install development and testing dependencies
RUN pip install -r requirements-dev.txt
RUN pip install -r requirements-tests.txt

# Install the project in editable mode
RUN pip install --no-build-isolation --editable .

# Run the test suite to verify the installation
RUN pytest