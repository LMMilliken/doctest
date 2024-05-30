FROM python:3.12-slim AS builder

RUN mkdir /app
WORKDIR /app

# Install git
RUN apt update && apt install -y git

# Clone the repository
RUN git clone <repository_url>

# Change to the repository directory
WORKDIR /app/<repository_name>

# Create a virtual environment
RUN python -m venv /opt/venv

# Install dependencies
RUN /opt/venv/bin/python -m pip install --upgrade pip
COPY requirements.txt /app/<repository_name>/
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Run the test suite
RUN /opt/venv/bin/python -m pytest
