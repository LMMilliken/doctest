FROM python:3.8

# Set the working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/commaai/openpilot.git .

# Install Poetry
RUN pip install poetry

# Install the project dependencies
RUN poetry install

# Run tests
RUN pip install pytest-randomly
RUN poetry run pytest --randomly-group 3
