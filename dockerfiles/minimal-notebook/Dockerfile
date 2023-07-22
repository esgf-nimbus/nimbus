ARG TAG=2023-05-01
FROM jupyter/base-notebook:${TAG}

LABEL org.opencontainers.image.source="https://github.com/esgf-nimbus/nimbus"
LABEL org.opencontainers.image.url="https://github.com/esgf-nimbus/nimbus/blob/main/dockerfiles/minimal-notebook/Dockerfile"

USER root

RUN groupadd -g 1026 climate && \
    usermod -a -G climate $NB_USER && \
    apt-get -q update && \
    DEBIAN_FRONTEND=noninteractive \
        apt-get install --yes --no-install-recommends \
        git \
        less \
        vim \
        unzip \
        rsync \
        openssh-client \
        curl \
        locate \
        htop \
        iputils-ping \
        dnsutils \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install nbgitpuller && \
    mkdir /notebooks

COPY notebooks /notebooks
COPY conda-envs /conda-envs

RUN --mount=type=cache,target=/opt/conda/pkgs \
    mamba env create -n dask-gateway -f /conda-envs/dask-gateway.yaml && \
    jupyter kernelspec install /opt/conda/envs/dask-gateway

USER $NB_USER
