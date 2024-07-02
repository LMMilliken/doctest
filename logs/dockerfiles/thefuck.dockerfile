FROM python:3.8

# Set the working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/nvbn/thefuck.git .

# Install via pip
RUN pip install thefuck

# Run the test suite
RUN pytest