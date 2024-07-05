# Use the official Python image from the Docker Hub
FROM python:3.9

# Install Poetry
RUN pip install poetry

# Install Git
RUN apt-get update && apt-get install -y git

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/Textualize/rich.git .

# Copy the Poetry lock file and pyproject.toml to the working directory
COPY poetry.lock pyproject.toml /app/

# Install project dependencies using Poetry
RUN poetry install

# Install pytest in case it is not included in the project's dependencies
RUN poetry run pip install pytest

# Run the test suite
RUN poetry run pytest