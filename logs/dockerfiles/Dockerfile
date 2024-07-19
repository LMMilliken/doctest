FROM python:3.9

WORKDIR /app

COPY requirements.txt .
COPY requirements-tests.txt .
COPY requirements-docs.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install pytest

RUN pytest