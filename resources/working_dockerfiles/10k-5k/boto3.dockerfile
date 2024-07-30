FROM python:3.8

COPY . /app/

WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

RUN pytest