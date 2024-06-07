FROM python:3.8

# Clone the repository
RUN git clone https://github.com/psf/black.git /black

# Set working directory
WORKDIR /black

# Install any necessary dependencies
RUN pip install -r requirements.txt

# Run the tests
RUN pytest -q --collect-only 2>&1 | head -n 1 | xargs pytest -sv