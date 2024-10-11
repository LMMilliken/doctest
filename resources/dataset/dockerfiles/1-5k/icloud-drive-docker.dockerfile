# Doesnt work with python 3.8
FROM python:3.10

COPY . /app/

WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install -r requirements-test.txt

# Commands to create required directories, taken from repo's workflows
RUN mkdir /config /icloud
RUN chown $(id -u) /config /icloud

RUN pytest