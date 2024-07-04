# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN apt-get update && apt-get install -y git \
    && git clone https://github.com/tiangolo/fastapi.git \
    && cd fastapi \
    && pip install -r requirements.txt

# Install pytest
RUN pip install pytest

# Copy the current directory contents into the container at /app
COPY . /app

# Run the test suite
RUN cd fastapi && pytest
