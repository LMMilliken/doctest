# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/home-assistant/core.git

# Change directory to the repository
WORKDIR /app/core

# Create a virtual environment
RUN python -m venv venv

# Activate the virtual environment
SHELL ["/bin/bash", "-c"]
RUN source venv/bin/activate

# Upgrade pip
RUN pip install --upgrade pip

# Install project dependencies using requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run the test suite
RUN pytest