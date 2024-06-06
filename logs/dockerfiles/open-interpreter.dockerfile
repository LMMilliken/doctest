# Start with Python base image
FROM python:3.8

# Clone the repository
RUN git clone https://github.com/OpenInterpreter/open-interpreter.git /app/open-interpreter

# Move into the repository directory
WORKDIR /app/open-interpreter

# Install poetry and the project dependencies
RUN pip install poetry
RUN poetry install

# Install pytest-randomly
RUN pip install pytest-randomly

# Run the test suite
CMD pytest --randomly-group 3
