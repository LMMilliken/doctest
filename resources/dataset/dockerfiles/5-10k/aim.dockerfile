FROM python:3.8

COPY . /app/

WORKDIR /app

RUN pip install -r tests/requirements.txt

RUN pytest