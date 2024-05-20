# Use an official Python runtime as a base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/tiangolo/fastapi.git .

# Install any necessary dependencies
RUN pip install -r ./requirements.txt

# Set the entrypoint to run tests
CMD ["python", "-m", "unittest"]