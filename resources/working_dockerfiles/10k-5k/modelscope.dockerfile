FROM python:3.8

COPY . /app/

WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install -r requirements/tests.txt

# make test does not work, tried to reference a file that does not exist
RUN make test