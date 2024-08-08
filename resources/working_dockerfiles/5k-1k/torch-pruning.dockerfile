FROM python:3.10
WORKDIR /app
COPY . /app/
# TIMEOUT
RUN pip install -r requirements.txt
RUN pytest