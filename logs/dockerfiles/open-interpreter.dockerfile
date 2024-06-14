FROM python:3.8

# Create app directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/OpenInterpreter/open-interpreter.git

# Move into the repository directory
WORKDIR /app/open-interpreter

# Install Poetry
RUN pip install poetry

# Install dependencies using Poetry
RUN poetry install

# Run the test suite
RUN poetry run pytest