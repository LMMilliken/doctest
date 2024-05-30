# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Clone the Home Assistant repository
RUN git clone https://github.com/home-assistant/core.git

# Change the working directory to the cloned repository
WORKDIR /app/core

# Install the dependencies using requirements.txt
RUN pip install -r requirements.txt

# Run the test suite
CMD ["python", "-m", "unittest"]
