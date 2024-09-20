# Use the official Python image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the entire repository into the container
COPY . /app/

# Set up the virtual environment
RUN python -m venv .venv

# Install required packages and editable install
RUN . .venv/bin/activate && \
    python -m pip install --no-cache-dir -r requirements-dev.txt && \
    python -m pip install --no-cache-dir -e .

# Run the test suite
RUN . .venv/bin/activate && pytest
