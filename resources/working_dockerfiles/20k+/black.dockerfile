FROM python:3.8

COPY . /app/

WORKDIR /app

RUN pip install -r test_requirements.txt
RUN pip install -e ".[d]"

RUN tox -e py