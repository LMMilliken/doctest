FROM python:3.8

RUN apt-get update && apt-get install -y git

WORKDIR /app

RUN git clone https://github.com/tqdm/tqdm.git .

RUN pip install -r requirements.txt

CMD ["python", "-m", "unittest"]