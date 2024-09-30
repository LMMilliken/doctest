# Use the official Python image as a base
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the entire repository into the container
COPY . /app/

# Install system dependencies required for Airflow (if needed)
# RUN apt-get update && apt-get install -y <required-packages>

# Install Poetry
RUN pip install poetry

# Install the dependencies including dev ones using make
RUN make install-poetry && make dev

# Run the test suite using Poetry
RUN poetry run pytest
