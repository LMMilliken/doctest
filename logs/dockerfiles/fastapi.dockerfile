FROM python:3.8

# Install system dependencies
RUN apt-get update && apt-get install -y git

# Clone the repository
RUN git clone https://github.com/tiangolo/fastapi.git /app

# Change the working directory
WORKDIR /app

# Create a virtual environment
RUN python -m venv venv

# Activate the virtual environment
SHELL ["/bin/bash", "-c"]
RUN source venv/bin/activate

# Install the project's dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Run the test suite
RUN pytest -q --collect-only 2>&1 | head -n 3 | xargs pytest -sv
