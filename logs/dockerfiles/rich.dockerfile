# Start with the official Python image
FROM python:3.9-slim

# Install git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Clone the repository
RUN git clone https://github.com/Textualize/rich.git

# Set the working directory
WORKDIR /rich

# Install dependencies using Poetry
RUN poetry install

# Install pytest
RUN pip install pytest

# Run tests
RUN pytest
