# Use an official Python runtime as a base image
FROM python:3

# Set the working directory in the container
WORKDIR /app

# Clone the openpilot repository from GitHub
RUN git clone https://github.com/commaai/openpilot.git

# Change the working directory to the cloned repository
WORKDIR /app/openpilot

# Install any required dependencies
RUN pip install -r requirements.txt

# Run the test suite
RUN pytest