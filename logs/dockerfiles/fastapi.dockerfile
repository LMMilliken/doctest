# Dockerfile

# Use an official Python runtime as a base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Clone the repository from GitHub
RUN git clone https://github.com/tiangolo/fastapi.git .

# Install the project dependencies
RUN pip install -r requirements.txt

# Set the command to run the project test suite
CMD ["pytest"]
