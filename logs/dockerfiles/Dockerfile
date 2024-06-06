FROM python:3.8

RUN git clone https://github.com/home-assistant/core.git /app/homeassistant

WORKDIR /app/homeassistant

RUN pip install -r requirements_all.txt

RUN pip install pytest-randomly

RUN pytest --randomly-group 3
