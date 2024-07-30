# Use the official Python image as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the entire repository into the container
COPY . /app/

# Install dependencies
RUN pip install --no-cache-dir pytest
RUN pip install --no-cache-dir -r requirements.txt

# Run the tests
RUN pytest