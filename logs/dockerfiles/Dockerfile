FROM continuumio/anaconda3

# Set the working directory
WORKDIR /app

# Copy the entire repository into the container
COPY . /app/

# Create a conda environment for the project
RUN conda create -n modelscope python=3.8 -y \
    && conda run -n modelscope pip install -U pip \
    && conda run -n modelscope pip install -r requirements/hub.txt \
    && conda run -n modelscope pip install modelscope \
    && conda run -n modelscope pip install -U openmim \
    && conda run -n modelscope pip uninstall mmcv -y \
    && conda run -n modelscope pip install mmcv-full \
    && conda run -n modelscope pip install modelscope[multi-modal] \
    && conda run -n modelscope pip install modelscope[nlp] -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html \
    && conda run -n modelscope pip install modelscope[cv] -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html \
    && conda run -n modelscope pip install modelscope[audio] -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html \
    && conda run -n modelscope pip install modelscope[science] -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html \
    && conda clean -afy

# Run the test suite to verify installation
RUN conda run -n modelscope pytest
