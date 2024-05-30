FROM python:3.8

# Install poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

# Setup working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/OpenInterpreter/open-interpreter.git .

# Install project dependencies
RUN poetry install

# Run the test suite
RUN pytest tests