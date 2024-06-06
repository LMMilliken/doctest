# Use the official Python image as base
FROM python:3

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/jhao104/proxy_pool.git .

# Install project dependencies
RUN pip install -r requirements.txt

# Install pytest-randomly
RUN pip install pytest-randomly

# Run the test suite
RUN pytest --randomly-group 3