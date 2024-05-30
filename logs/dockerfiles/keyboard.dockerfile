# Use the official Python image from the Docker Hub
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Clone the repository from the source
RUN git clone https://github.com/your-username/your-repo.git

# Set the working directory to the cloned repository
WORKDIR /app/your-repo

# Run the test suite of the repository to verify installation
RUN make test