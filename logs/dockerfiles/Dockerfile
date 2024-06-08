FROM python:3.8

# Clone the repository
RUN git clone https://github.com/explosion/spaCy.git

# Move into the cloned repository
WORKDIR spaCy

# Install the required dependencies
RUN pip install -r requirements.txt

# Change the working directory to the 'spacy' directory
WORKDIR spacy

# Run the test suite
RUN pytest -v