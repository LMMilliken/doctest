# Use a base image with Python 3.7+ (newer version if necessary)
FROM python:3.8-slim

# Install git and required compilers, and cleanup
RUN apt-get update && apt-get install -y git gcc g++ make && \
    pip install cython && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/explosion/spaCy.git && \
    cd spaCy && \
    pip install --no-cache-dir -r requirements.txt && \
    if [ -f requirements_dev.txt ]; then pip install --no-cache-dir -r requirements_dev.txt; fi && \
    pip install pytest && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Navigate to the repository directory
WORKDIR /app/spaCy

# Set environment variable for parallel build jobs if necessary
ENV SPACY_NUM_BUILD_JOBS=4

# Run the test suite
RUN pytest

# Clean up unused apt packages
RUN apt-get clean && rm -rf /var/lib/apt/lists/*