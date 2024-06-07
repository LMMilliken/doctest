# Use the official Python image as a base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Clone the repository from GitHub
RUN git clone https://github.com/OpenInterpreter/open-interpreter.git

# Move into the cloned repository directory
WORKDIR /app/open-interpreter

# Install the project dependencies using Poetry
RUN pip install poetry
RUN poetry install

# Run the test suite
RUN pytest -q --collect-only 2>&1 | head -n 3 | xargs pytest -sv
