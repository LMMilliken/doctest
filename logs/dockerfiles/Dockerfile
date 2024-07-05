# First stage: Build the application
FROM python:3.9-slim as builder

# Set the working directory inside the container
WORKDIR /usr/src/app

# Install required system packages for building
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone the spaCy repository
RUN git clone https://github.com/explosion/spaCy.git

# Set the working directory to the cloned repository
WORKDIR /usr/src/app/spaCy

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Second stage: Main
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /usr/src/app/spaCy

# Copy only the required files from the builder stage
COPY --from=builder /usr/src/app/spaCy /usr/src/app/spaCy

# Install pytest for running tests
RUN pip install pytest

# If additional requirements are needed for testing, they need to be installed here
RUN if [ -f build-constraints.txt ]; then pip install --no-cache-dir -r build-constraints.txt; fi

# Run the tests
RUN pytest
