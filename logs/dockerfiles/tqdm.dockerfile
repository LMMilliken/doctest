FROM python:3.8

# Clone the repository
RUN git clone https://github.com/tqdm/tqdm.git /tqdm

# Move into the repository
WORKDIR /tqdm

# Install the repository
RUN pip install .

# Run the test suite
RUN pytest -q --collect-only 2>&1 | head -n 3 | xargs pytest -sv
