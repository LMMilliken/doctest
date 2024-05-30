# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/username/repository.git

# Change the working directory to the cloned repo
WORKDIR /app/repository

# Install the project dependencies
RUN pip install -r requirements.txt

# Run the test suite
CMD ["pytest"]