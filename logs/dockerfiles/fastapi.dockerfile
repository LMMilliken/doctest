# Use the official Python image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/tiangolo/fastapi.git

# Move into the repository directory
WORKDIR /app/fastapi

# Install project dependencies
RUN pip install -r requirements.txt

# Run the test suite
RUN python -m pytest