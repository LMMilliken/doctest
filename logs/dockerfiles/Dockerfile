FROM python:3.8

# Set the working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/explosion/spaCy.git ./

# Move into the repository directory
WORKDIR /app/spaCy

# Install dependencies using requirements.txt
COPY requirements.txt ./
RUN pip install -r ./requirements.txt

# Run the test suite
RUN python -m pytest