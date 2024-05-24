# Use the official Python image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . /app

# Install Poetry and dependencies
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

# Run the repo's test suite at the end of the build process
RUN pytest