FROM python:3.11.8

# Install Poetry
RUN pip install poetry

# Clone the repository
RUN git clone https://github.com/OpenInterpreter/open-interpreter.git

# Change the working directory to the cloned repository
WORKDIR /open-interpreter

# Copy poetry.lock and pyproject.toml for dependency installation
COPY poetry.lock pyproject.toml .

# Install dependencies using Poetry
RUN poetry install

# Install pytest
RUN pip install pytest

# Run the tests
RUN pytest
