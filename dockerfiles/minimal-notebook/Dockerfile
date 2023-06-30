ARG TAG=2023-05-01
FROM jupyter/base-notebook:${TAG}

USER root

ENV CONTAINER_VERSION 0.1.3

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

COPY notebooks/* /notebooks

USER $NB_USER
