FROM python:3.11

COPY . /app/

WORKDIR /app

RUN pip install -e .
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt
RUN pip install -r requirements-test.txt

RUN make test