ARG TAG=2023.1.1
FROM ghcr.io/dask/dask-gateway:${TAG}

ENV CONTAINER_VERSION 0.1.0

RUN pip install --upgrade pip && \
    pip install "bokeh<3"
