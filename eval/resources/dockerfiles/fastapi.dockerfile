# Use the official image as a base
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/tiangolo/fastapi.git

# Move into the cloned repository directory
WORKDIR /app/fastapi

# Install pytest-randomly
RUN pip install pytest-randomly

# Run the test suite using pytest-randomly
RUN pytest --randomly-group 3