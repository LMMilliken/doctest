FROM python:3.11

COPY . /app/

WORKDIR /app

RUN apt update && apt install -y ffmpeg

RUN pip install poetry

RUN poetry install

RUN poetry run pytest