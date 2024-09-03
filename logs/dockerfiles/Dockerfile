# Use the official Python image as a base
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the entire repository into the container
COPY . /app/

# Install Poetry
RUN pip install --no-cache-dir poetry

# Install all dependencies including development ones
RUN make install-poetry && make dev

# Run the test suite to verify successful installation
RUN poetry run pytest
