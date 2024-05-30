# Use the official Python image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN git clone <repository_url> .

# Run the test suite
CMD ["pytest"]
