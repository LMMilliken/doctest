# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install git
RUN apt-get update && apt-get install -y git

# Clone the repository
RUN git clone https://github.com/home-assistant/core.git

# Set the working directory to the cloned repository
WORKDIR /usr/src/app/core

# Copy the requirements files
COPY requirements.txt requirements.txt
COPY requirements_all.txt requirements_all.txt
COPY requirements_test.txt requirements_test.txt
COPY requirements_test_all.txt requirements_test_all.txt
COPY requirements_test_pre_commit.txt requirements_test_pre_commit.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements_all.txt
RUN pip install --no-cache-dir -r requirements_test.txt
RUN pip install --no-cache-dir -r requirements_test_all.txt
RUN pip install --no-cache-dir -r requirements_test_pre_commit.txt

# Install pytest
RUN pip install pytest

# Run the test suite
RUN pytest
