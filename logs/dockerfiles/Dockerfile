FROM python:3.8

# Set the working directory
WORKDIR /app

# Copy the entire repository
COPY . /app/

# Install Poetry
RUN pip install poetry

# Install project dependencies, including optional airflow dependencies
RUN poetry install --with airflow
RUN make dev

# Run the test suite using Poetry
RUN poetry run pytest
