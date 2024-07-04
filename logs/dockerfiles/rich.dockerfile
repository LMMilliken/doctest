FROM python:3.10-slim

# Install git
RUN apt-get update && apt-get install -y git

# Install Poetry
RUN pip install poetry

# Clone the repository
RUN git clone https://github.com/Textualize/rich.git

# Set the working directory
WORKDIR rich

# Install dependencies with Poetry
RUN poetry install

# Install pytest to run the tests
RUN poetry add pytest

# Run the test suite
RUN poetry run pytest
