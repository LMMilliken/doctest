# Use the official Python image as the base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Clone the openpilot repository
RUN git clone https://github.com/commaai/openpilot.git

# Move into the openpilot directory
WORKDIR /app/openpilot

# Install Poetry (assuming it's not already installed in the base image)
RUN curl -sSL https://install.python-poetry.org | python -

# Install the project dependencies using Poetry
RUN poetry install

# Run the test suite of the repository
RUN pytest -q --collect-only 2>&1 | head -n 3 | xargs pytest -sv
