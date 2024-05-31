FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Clone the repository
cmd git clone https://github.com/jhao104/proxy_pool.git .

# Install the dependencies
cmd pip install -r requirements.txt

# Run the test suite
cmd python test.py
