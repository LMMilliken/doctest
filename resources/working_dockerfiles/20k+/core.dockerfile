FROM python:3.12

COPY . /app/

WORKDIR /app

RUN pip install -r requirements_all.txt
RUN pip install -r requirements_test_all.txt

RUN python -m unittest discover