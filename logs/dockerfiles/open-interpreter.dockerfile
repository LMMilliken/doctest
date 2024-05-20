# Use an official Python runtime as a base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/OpenInterpreter/open-interpreter.git .

# Install dependencies using Poetry
RUN pip install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false \n && poetry install --no-dev

# Run tests
RUN pytest