FROM python:3.8

# Clone the repository
RUN git clone https://github.com/jhao104/proxy_pool.git

# Move into the repository directory
WORKDIR /proxy_pool

# Install dependencies
RUN pip install -r requirements.txt

# Run the test suite
RUN pytest