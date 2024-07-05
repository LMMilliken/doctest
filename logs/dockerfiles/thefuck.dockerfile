# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install git
RUN apt-get update && apt-get install -y git

# Clone the repository
RUN git clone https://github.com/nvbn/thefuck.git

# Change directory to the cloned repository
WORKDIR /usr/src/app/thefuck

# Copy requirements.txt and install any needed packages specified in it
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure pytest is installed
RUN pip install pytest

# Run the tests
RUN pytest