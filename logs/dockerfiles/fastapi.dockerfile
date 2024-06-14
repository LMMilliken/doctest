FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Clone the FastAPI repository
RUN git clone https://github.com/tiangolo/fastapi.git .

# Set up the working environment for the repository
RUN python -m venv venv
RUN /bin/bash -c 'source venv/bin/activate'
RUN pip install -r requirements.txt

# Run the repository's test suite
RUN pytest