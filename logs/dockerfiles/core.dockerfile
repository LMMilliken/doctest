FROM python:3.8

# Clone the repository
RUN git clone https://github.com/home-assistant/core.git /app/home-assistant

# Move into the repository directory
WORKDIR /app/home-assistant

# Install dependencies from requirements.txt
COPY requirements.txt /app/home-assistant/requirements.txt
RUN pip install -r requirements.txt

# Run the test suite
RUN pytest