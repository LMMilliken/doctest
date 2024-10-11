FROM python:3.8

COPY . /app/

WORKDIR /app

RUN pip install ctc-segmentation
RUN pip install -r requirements.txt
RUN pip install torch==2.2.1+cpu torchaudio==2.2.1+cpu --extra-index-url https://download.pytorch.org/whl/cpu k2==1.24.4.dev20240223+cpu.torch2.2.1 --find-links https://k2-fsa.github.io/k2/cpu.html kaldilm==1.15.1 spacy==3.7.4 flair==0.13.1 gensim==4.3.2
RUN pip install -e .

RUN pytest tests