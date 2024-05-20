# Use Python base image
FROM python:3.8

# Set the working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/jhao104/proxy_pool.git .

# Install dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Run tests
COPY . ./
RUN python test.py
