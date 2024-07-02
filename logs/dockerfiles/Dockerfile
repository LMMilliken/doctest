# Use the official Python image as the base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/OpenInterpreter/open-interpreter.git

# Move into the project directory
WORKDIR /app/open-interpreter

# Install Poetry
RUN pip install poetry

# Install the project's dependencies using Poetry
RUN poetry install

# Run the test suite
# Replace the line below with the appropriate command to run the tests
# For example, if the tests are executed using a script file:
# RUN sh run_tests.sh

# If the tests are run using a python module, you can run them using the following command:
# RUN python -m pytest

# Alternatively, if the tests are not using pytest, replace with the appropriate test command
RUN echo 'No test command specified'