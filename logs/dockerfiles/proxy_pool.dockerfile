# Use an official Python runtime as a base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Clone the repository from the provided URL
RUN git clone https://github.com/jhao104/proxy_pool.git /app/proxy_pool

# Move into the project directory
WORKDIR /app/proxy_pool

# Install the Python packages using the requirements.txt file
RUN pip install -r requirements.txt

# Update the project configuration if required
# Example: COPY config/settings.py /app/proxy_pool/

# Run the test suite at the end of the build process
RUN pytest -q --collect-only 2>&1 | head -n 3 | xargs pytest -sv