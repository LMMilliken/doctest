# Step 1: Start from a base Python image
FROM python:3.9

# Step 2: Install Poetry
RUN pip install poetry

# Step 3: Set the working directory for the application
WORKDIR /app

# Step 4: Copy the entire repository into the container
COPY . /app/

# Step 5: Install the project dependencies using Poetry
RUN poetry install

# Step 6: Ensure pytest is installed to run tests
RUN poetry run pip install pytest

# Step 7: Run the project's test suite to verify installation
RUN poetry run pytest