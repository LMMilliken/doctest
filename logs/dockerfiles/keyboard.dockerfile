FROM python:3.8

# Clone the repository
RUN git clone https://github.com/boppreh/keyboard.git

# Set the working directory
WORKDIR /keyboard

# Install any project dependencies
# No dependency installation needed for this project

# Run the test suite
RUN pytest -q --collect-only 2>&1 | head -n 3 | xargs pytest -sv
