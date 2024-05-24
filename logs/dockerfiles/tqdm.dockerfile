FROM python:3.8

# Clone the repository
git clone https://github.com/tqdm/tqdm.git /tqdm
WORKDIR /tqdm

# Run the test suite
CMD ["python", "-m", "unittest", "-v", "tqdm"]
