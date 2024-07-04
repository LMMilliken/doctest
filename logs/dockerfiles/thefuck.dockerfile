# Use the official Python image from the Docker Hub
FROM python:3.8-slim

# Install necessary system packages
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/nvbn/thefuck.git

# Change to the cloned repository directory
WORKDIR /app/thefuck

# Copy the requirements file to the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install pytest and other dev dependencies if necessary
RUN pip install --no-cache-dir pytest

# Run the tests
RUN pytest

# Set default command (optional)
CMD ["/bin/bash"]
