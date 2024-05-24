# Use the official Python image as the base image
FROM python:3.12-slim AS builder

# Set the working directory in the container
WORKDIR /app

# Copy the content of the repository to the working directory
COPY . /app/

# Set up the virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install build tools
RUN apt-get update && apt-get install -y build-essential

# Install project dependencies
RUN pip install --upgrade pip
RUN pip install -r /app/test_requirements.txt

# Run the test suite
CMD ["python", "/app/scripts/run_tests.py"]