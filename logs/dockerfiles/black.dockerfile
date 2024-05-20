# Use the official image as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/psf/black.git

# Change the working directory to the cloned repository
WORKDIR /app/black

# Install any necessary dependencies
RUN pip install -r test_requirements.txt

# Run tests to verify the installation
RUN pytest