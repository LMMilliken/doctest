FROM python:3.10

COPY . /app/

WORKDIR /app

RUN apt-get update && apt-get install libgl1  -y
RUN pip install onnxruntime
RUN pip install -r requirements.txt

RUN python -m unittest tests/test_utils/test_general.py