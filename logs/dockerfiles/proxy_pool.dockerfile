# Use an official Python runtime as a base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Clone the repository from the GitHub URL
RUN git clone <URL> .

# Install any required dependencies
RUN pip install -r requirements.txt

# Run the test suite
CMD ["python", "test.py"]