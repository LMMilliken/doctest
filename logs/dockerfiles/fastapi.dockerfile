FROM python:3.8

# Set the working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/tiangolo/fastapi.git .

# Set up the working environment
RUN python3 -m venv venv

# Activate the virtual environment
SHELL ["/bin/bash", "-c"]
RUN source venv/bin/activate

# Install project dependencies
RUN pip install -r requirements.txt

# Run the test suite
RUN pytest