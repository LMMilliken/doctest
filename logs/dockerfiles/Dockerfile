# Use an official Ubuntu base image
FROM ubuntu:20.04

# Set the working directory
WORKDIR /app

# Install necessary packages
RUN apt-get update && \
    apt-get install -y \
    git \
    git-lfs \
    python3 \
    python3-pip \
    python3-setuptools \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the local repository contents into the container
COPY . /app/

# Install dependencies
RUN chmod +x tools/ubuntu_setup.sh && \
    ./tools/ubuntu_setup.sh

# Build the project
RUN scons -j$(nproc)

# Run the test suite to verify installation
RUN pytest
