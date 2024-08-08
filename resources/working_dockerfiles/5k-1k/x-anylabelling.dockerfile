FROM python:3.10

COPY . /app/

WORKDIR /app

# install onnxruntime, as suggested in docs
RUN pip install onnxruntime

RUN pip install -r requirements.txt
# RUN pip install -r requirements-dev.txt

RUN python -m unittest tests/unit_tests/test_general.py