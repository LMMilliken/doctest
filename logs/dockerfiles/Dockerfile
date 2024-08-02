FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the entire repository into the container
COPY . /app/

# Install dependencies from requirements files
RUN pip install -r requirements.txt \
    && pip install -r requirements-test.txt

# Run the tests
RUN pytest