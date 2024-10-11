FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install poetry
RUN poetry install 
RUN pip install wheel
RUN pip install --no-build-isolation --editable .
RUN pip install pytest
RUN pytest
