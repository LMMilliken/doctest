FROM python:3.9

COPY . /app/

WORKDIR /app

RUN apt update && apt install -y llvm
RUN pip install git+https://github.com/numba/llvmlite.git@v0.44.0dev0
RUN pip install numpy
RUN python setup.py build_ext --inplace

RUN python -m numba.runtests -m --random 0.1