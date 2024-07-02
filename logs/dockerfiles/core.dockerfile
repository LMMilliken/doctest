FROM python:3.8

# Create app directory
WORKDIR /usr/src/app

# Clone the repository
RUN git clone https://github.com/home-assistant/core.git .

# Install dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Run the tests
RUN pytest