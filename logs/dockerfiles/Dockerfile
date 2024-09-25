# Use the official Python image as a base
FROM python:3.8

# Set the working directory
WORKDIR /app

# Copy the entire repository into the container
COPY . /app/

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN make install-poetry && poetry install

# Run the test suite
RUN poetry run pytest
