FROM python:3.10
WORKDIR /app
COPY . /app/

RUN pip install -e .
RUN pip install -r requirements-dev.txt
RUN pip install -r requirements-ci.txt

RUN python -m pytest tests -p no:warnings -x