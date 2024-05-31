# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/tiangolo/fastapi.git

# Move into the cloned repository
WORKDIR /app/fastapi

# Install the dependencies
RUN pip install -r requirements.txt

# Run the test suite
CMD ["pytest"]