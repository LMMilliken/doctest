# Use the official Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the entire repository into the container
COPY . /app/

# Install Poetry
RUN pip install poetry

# Install all dependencies including extras
RUN poetry install --all-extras

# Run the test suite to verify installation
RUN poetry run pytest