FROM python:3.8

# Clone the repository
RUN git clone https://github.com/Textualize/rich.git

# Move into the repository
cd rich

# Install Poetry
RUN pip install poetry

# Install dependencies using Poetry
cd rich
RUN poetry install

# Run the test suite
RUN poetry run pytest