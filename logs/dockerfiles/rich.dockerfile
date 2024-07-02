FROM python:3.8

# Install Poetry
RUN pip install poetry

# Set the working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/Textualize/rich.git .

# Install dependencies
RUN poetry install

# Run the test suite
RUN poetry run pytest