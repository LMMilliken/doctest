FROM python:3.8

# Set working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/nvbn/thefuck.git

# Change directory to the repository
WORKDIR /app/thefuck

# Install the project
RUN pip install .

# Run the test suite
RUN pytest