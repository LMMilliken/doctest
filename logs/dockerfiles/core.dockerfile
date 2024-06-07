# Use the official Python image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/home-assistant/core.git .

# Install the project's dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Run the test suite
RUN pytest -q --collect-only 2>&1 | head -n 3 | xargs pytest -sv
