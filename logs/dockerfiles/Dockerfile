# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy the entire repository into the container
COPY . /app/

# Install dependencies
RUN pip install "fastapi[standard]"
RUN pip install -r requirements-tests.txt

# Run tests
RUN pytest