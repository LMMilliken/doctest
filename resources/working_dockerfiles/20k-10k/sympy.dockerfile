FROM python:3.11

COPY . /app/

WORKDIR /app

RUN pip install mpmath

RUN python setup.py test