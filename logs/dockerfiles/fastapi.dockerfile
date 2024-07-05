# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Clone the repository
RUN git clone https://github.com/tiangolo/fastapi.git

# Set the working directory to the cloned repository
WORKDIR /app/fastapi

# Copy the requirements.txt from the cloned repository
COPY requirements.txt /app/fastapi/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install pytest to run tests
RUN pip install pytest

# Run the test suite
RUN pytest
