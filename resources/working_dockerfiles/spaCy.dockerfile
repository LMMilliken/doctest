FROM python:3.8

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir -U pip setuptools

RUN pip install -r requirements.txt

RUN pip install wheel 

RUN pip install --no-build-isolation --editable .

RUN pytest