FROM python:3.8

# Install Poetry
curl -sSL https://install.python-poetry.org | python -

# Set the working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/OpenInterpreter/open-interpreter.git .

# Install project dependencies
RUN poetry install

# Run the tests
RUN poetry run pytest