# Use an official Python runtime as a base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Clone the repository from GitHub
RUN git clone https://github.com/jhao104/proxy_pool.git .

# Install project dependencies
RUN pip install -r requirements.txt

# Run the test suite
RUN pytest -q --collect-only 2>&1 | head -n 3 | xargs pytest -sv
