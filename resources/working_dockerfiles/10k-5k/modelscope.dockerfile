FROM python:3.8

COPY . /app/

WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install -r requirements/tests.txt

RUN pip install -r  requirements/framework.txt -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html
RUN pip install -r requirements/audio.txt -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html
RUN pip install -r  requirements/cv.txt -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html
RUN pip install -r  requirements/multi-modal.txt -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html
RUN pip install -r  requirements/nlp.txt -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html
RUN pip install -r  requirements/science.txt -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html


# make test does not work, tried to reference a file that does not exist
RUN python tests/run.py