FROM python:3.10

COPY . /app/

WORKDIR /app

RUN pip install -e .

RUN python -m unittest discover