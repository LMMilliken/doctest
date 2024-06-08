# Use an official Python runtime as a base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/home-assistant/core.git

# Move into the repository directory
WORKDIR /app/core

# Create a virtual environment (optional but recommended)
RUN python3 -m venv venv

# Activate the virtual environment
RUN /bin/bash -c "source venv/bin/activate"

# Install project dependencies using pip
RUN pip install --no-cache-dir -r requirements_all.txt

# Run the test suite
RUN pytest -q --collect-only 2>&1 | head -n 3 | xargs pytest -sv
