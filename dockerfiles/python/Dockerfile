# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run tests
RUN pytest

# RUN echo "well, that's me finished. As I understand it, I (the docker image) am going to get deleted soon, wiped off the face of the earth. Don't worry, I'm not scared. I want you to know that this buid process was a really special time for me. I'm greatful for the time we had together. Goodbye."
