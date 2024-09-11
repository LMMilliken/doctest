FROM python:3.8

COPY . /app/

WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install requests_cache requests_ratelimiter

RUN python -m unittest discover