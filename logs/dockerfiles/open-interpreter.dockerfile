# Use the official Python image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . .

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python -

# Install project dependencies using Poetry
RUN poetry install

# Run the test suite
RUN poetry run pytest