FROM python:3.9

COPY . /app/

WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install -e .

RUN python -m unittest discover