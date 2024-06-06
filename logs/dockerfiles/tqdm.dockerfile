# Use the official image as a parent image
FROM python:3

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/tqdm/tqdm.git

# Move into the repository directory
WORKDIR /app/tqdm

# Install pytest-randomly
RUN pip install pytest-randomly

# Run the test suite
RUN pytest --randomly-goup 3
