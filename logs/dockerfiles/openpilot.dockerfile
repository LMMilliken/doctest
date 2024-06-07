FROM python:3.8

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository
RUN git clone https://github.com/commaai/openpilot.git /app/openpilot

# Set the working directory
WORKDIR /app/openpilot

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
RUN poetry install

# Run the test suite
RUN pytest -q --collect-only 2>&1 | head -n 3 | xargs pytest -sv
