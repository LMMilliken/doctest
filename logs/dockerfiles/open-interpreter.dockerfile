# Use a Python base image with Python 3.8
FROM python:3.8

# Set the working directory
WORKDIR /app

# Copy the entire repository contents to the container
COPY . /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python -

# Install dependencies using Poetry
RUN poetry install

# Run the test suite
RUN poetry run pytest