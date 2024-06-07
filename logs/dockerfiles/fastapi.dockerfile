# Use the official image as a parent image
FROM python:3.8

# Set the working directory within the container
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/tiangolo/fastapi.git .

# Install project dependencies
RUN pip install -r requirements.txt

# Run the test suite
RUN pytest -q --collect-only 2>&1 | head -n 3 | xargs pytest -sv
