FROM python:3.10

COPY . /app/

WORKDIR /app

RUN pip install -e .
RUN pip install -r requirements-dev.txt

RUN python -m pytest -v tests/model/test_core.py 