FROM python:3.8

RUN apt-get update && apt-get install -y git

RUN git clone https://github.com/jhao104/proxy_pool.git /app

WORKDIR /app

RUN pip install -r requirements.txt

RUN pip install pytest-randomly

RUN pytest --randomly-group 3
