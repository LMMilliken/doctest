# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the entire repository into the container
COPY . /app/

# Install dependencies
RUN pip install -r requirements.txt

# Install the current package in editable mode
RUN pip install --no-build-isolation --editable .

# Run the test suite
RUN pytest
