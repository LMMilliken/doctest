# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /usr/src/app

# Install necessary system packages
RUN apt-get update && apt-get install -y \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository
RUN git clone https://github.com/nvbn/thefuck.git

# Set the working directory to the cloned repository
WORKDIR /usr/src/app/thefuck

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install pytest
RUN pip install pytest

# Run the test suite
RUN pytest
