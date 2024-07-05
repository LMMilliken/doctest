FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install required system packages
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone the spaCy repository
RUN git clone https://github.com/explosion/spaCy.git

# Set the working directory to the cloned repository
WORKDIR /usr/src/app/spaCy

# Copy requirements.txt into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install pytest for running tests
RUN pip install pytest

# Run the tests
RUN pytest