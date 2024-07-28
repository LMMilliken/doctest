FROM continuumio/miniconda3

# Set the working directory
WORKDIR /app

# Copy the entire repository into the container
COPY . /app/

# Install the base dependencies
RUN conda install -c conda-forge python=3.7 pip ipykernel ipywidgets setuptools toml

# Install test environment managers and other necessary tools
RUN pip install pre-commit tox asv pytest pytest-cov pytest-timeout pytest-asyncio nbval coverage

# Install the package itself
RUN pip install .

# Run the test suite to verify installation
RUN pytest