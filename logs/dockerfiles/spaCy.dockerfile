FROM python:3.8

# Set the working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/explosion/spaCy.git .

# Set up a virtual environment
RUN python3 -m venv venv

# Activate the virtual environment
RUN /bin/bash -c "source venv/bin/activate"

# Install the project dependencies
RUN pip install -r requirements.txt

# Run the test suite
RUN pytest