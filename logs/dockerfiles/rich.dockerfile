FROM python:3.8

# Set the working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/Textualize/rich.git .

# Install Poetry
RUN pip install poetry

# Set up the repository
RUN poetry install

# Run the test suite
RUN pytest