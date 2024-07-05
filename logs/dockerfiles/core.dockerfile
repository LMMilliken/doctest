# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install git
RUN apt-get update && apt-get install -y git

# Set the working directory in the container
WORKDIR /usr/src/app

# Clone the repository
RUN git clone https://github.com/home-assistant/core.git

# Change working directory to the cloned repository
WORKDIR /usr/src/app/core

# Copy the requirements file into the container at /usr/src/app
COPY requirements.txt .

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install pytest
RUN pip install pytest

# Run the test suite
RUN pytest
