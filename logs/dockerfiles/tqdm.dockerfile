# Use an official Python runtime as a base image
FROM python:3

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/tqdm/tqdm.git

# Change the working directory to the cloned repo
WORKDIR /app/tqdm

# Install the required dependencies
RUN pip install .

# Run the test suite
RUN python -m unittest discover -s tests
