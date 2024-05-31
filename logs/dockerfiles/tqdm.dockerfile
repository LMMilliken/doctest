# Use the official image as a parent image
FROM python:3.7

# Clone the repository
RUN git clone https://github.com/tqdm/tqdm.git /tqdm

# Set the working directory to the repository
WORKDIR /tqdm

# Run the test suite
RUN python -m unittest discover
