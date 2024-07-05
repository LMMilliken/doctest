FROM python:3.9-slim

# Install necessary system packages
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository
RUN git clone https://github.com/OpenInterpreter/open-interpreter.git

# Set working directory
WORKDIR /open-interpreter

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry install

# Install pytest
RUN pip install pytest

# Run the tests
RUN pytest