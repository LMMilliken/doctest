FROM python:3.8

RUN apt-get update && apt-get install -y git

RUN git clone https://github.com/boppreh/keyboard.git /app
WORKDIR /app

RUN pip install pytest
RUN pip install -e .
RUN pip install pytest-randomly

CMD ["pytest", "--randomly-group", "3"]
