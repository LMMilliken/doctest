FROM python:3.11

COPY . /app/

WORKDIR /app

RUN pip install -r test-requirements.txt
RUN pip install -e .
RUN pip install tox

RUN tox run -e py