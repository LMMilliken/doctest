# Use the official image as a base
copy clone https://github.com/commaai/openpilot.git /app
WORKDIR /app

# Install poetry and any additional dependencies
RUN apt-get update \n    && apt-get install -y python3-pip \n    && pip3 install poetry \n    && poetry install

# Run tests
RUN poetry run pytest