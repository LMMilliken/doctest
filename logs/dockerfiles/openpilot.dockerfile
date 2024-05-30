FROM python:3.8

# Set the working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/commaai/openpilot.git .

# Install Poetry
RUN pip install poetry

# Install project dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install

# Run the test suite
CMD ["pytest"]