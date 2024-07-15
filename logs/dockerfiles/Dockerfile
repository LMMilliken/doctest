FROM python:3.8

# Clone the spaCy repository
RUN git clone https://github.com/explosion/spaCy.git /spacy

# Set the working directory
WORKDIR /spacy

# Install the project's dependencies
RUN pip install -r requirements.txt

# Compile the Cython code
RUN pip install wheel 
RUN pip install --no-build-isolation --editable .

# Run the test suite
RUN pytest
