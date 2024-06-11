# Use the official Python image as the base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/OpenInterpreter/open-interpreter.git /app/open-interpreter

# Move into the repository directory
WORKDIR /app/open-interpreter

# Install Poetry
RUN pip install poetry

# Install dependencies using Poetry
RUN poetry install

# Run the test suite
RUN pytest