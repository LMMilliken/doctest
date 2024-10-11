# Use the official Python image as base
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the entire repository into the container
COPY . /app/

# run make command to install dependencies
RUN make init

# run make command to run tests
RUN make test
