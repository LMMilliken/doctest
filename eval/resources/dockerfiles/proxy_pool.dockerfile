FROM python:3.8

# Set working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/jhao104/proxy_pool.git .

# Install dependencies
RUN pip install -r requirements.txt

# Run the test suite
RUN pytest -q --collect-only 2>&1 | head -n 1 | xargs pytest -sv