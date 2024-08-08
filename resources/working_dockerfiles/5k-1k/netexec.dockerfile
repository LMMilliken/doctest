FROM python:3.11

COPY . /app/

WORKDIR /app

# pipx being used as recommended in the wiki
RUN apt-get update
RUN apt install -y pipx
RUN pipx install poetry

# Dynamic versioning also recommended in the wiki
RUN poetry self add "poetry-dynamic-versioning[plugin]"
RUN poetry dynamic-versioning enable

RUN poetry install

RUN poetry run pytest