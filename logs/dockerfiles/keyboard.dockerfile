# Dockerfile

# Use an official Python runtime as a base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/boppreh/keyboard.git .

# Run any necessary installation commands
# Based on the Makefile contents, it seems that the installation steps are integrated into the make tasks.
# We can execute the build task to take care of installation.
RUN make build

# Run tests to verify the installation
RUN pytest