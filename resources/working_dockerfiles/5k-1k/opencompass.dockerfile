FROM python:3.10

COPY . /app/

WORKDIR /app

# RUN pip install -r requirements.txt

# FAILS DUE TO TIMEOUT (>10 mins)
RUN pip install -e .

RUN python -m unittest discover