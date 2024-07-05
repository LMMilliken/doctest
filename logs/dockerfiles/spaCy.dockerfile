# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory in the container
WORKDIR /usr/src/app

# Install git
RUN apt-get update && apt-get install -y git

# Clone the repository
RUN git clone https://github.com/explosion/spaCy.git

# Set the working directory to the cloned repository
WORKDIR /usr/src/app/spaCy

# Copy the requirements file into the container (if available)
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install pytest for testing (if not already included in requirements)
RUN pip install pytest

# Run the test suite
RUN pytest