# Use the official Python image from the Docker Hub
copy
FROM python:3.8

# Set the working directory inside the container
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/home-assistant/core.git

# Change working directory to the repository directory
WORKDIR /app/core

# Install the required packages using the requirements.txt file
RUN pip install -r requirements.txt

# Run the test suite
RUN pytest
