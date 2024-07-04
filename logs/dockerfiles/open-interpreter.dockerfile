# Use the official Python base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install Poetry
RUN pip install poetry

# Set the working directory
WORKDIR /app

# Clone the repository
RUN apt-get update && \
    apt-get install -y git && \
    git clone https://github.com/OpenInterpreter/open-interpreter.git .

# Move into the repository directory
WORKDIR /app/open-interpreter

# Install dependencies
RUN poetry install

# Install pytest in case it's not included in the dependencies
RUN poetry add pytest

# Run the tests
RUN poetry run pytest