FROM python:3.8

# Set the working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/tiangolo/fastapi.git

# Move into the cloned repository directory
WORKDIR /app/fastapi

# Install project dependencies using the requirements file
RUN pip install -r requirements.txt

# Run the test suite
RUN pytest