# Start from the official Python base image
FROM python:3.9-slim

# Update the package lists and install system dependencies
# RUN apt-get update && apt-get install -y python3-dev python3-pip python3-setuptools

# Set the working directory to /app
WORKDIR /app

# Copy the entire repository into the container
COPY . /app/

# Install the Python dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install the package itself to ensure all dependencies are included
RUN pip install wheel && pip install --no-build-isolation --editable .

# Install pytest to run the tests
RUN pip install pytest

# Run the test suite
RUN pytest