# Use the official Python image
FROM python:3.8

# Set the working directory within the container
WORKDIR /app

# Clone the spaCy repository
RUN git clone https://github.com/explosion/spaCy.git .

# Install the project's dependencies
RUN pip install -r requirements.txt

# Run the test suite
RUN pytest
