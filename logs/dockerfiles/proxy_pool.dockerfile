FROM python:3.6

# Set the working directory in the container
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/jhao104/proxy_pool.git .

# Copy the requirements.txt file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Run the test suite
CMD ["python", "test.py"]