# Use the official Python image from the Docker Hub
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Install git
RUN apt-get update && apt-get install -y git

# Clone the repository
RUN git clone https://github.com/nvbn/thefuck.git

# Change the working directory to the cloned repository
WORKDIR /app/thefuck

# Copy the application's requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install pytest for running tests (in case it's not included in the requirements)
RUN pip install pytest

# Run the application's test suite to verify installation
RUN pytest
