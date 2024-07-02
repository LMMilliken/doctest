# Use the official Python image from the Docker Hub
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/Textualize/rich.git

# Change directory to the cloned repository
WORKDIR /app/rich

# Install Poetry
RUN pip install poetry

# Install the project dependencies using Poetry
RUN poetry install

# Run the test suite
RUN poetry run pytest