ARG TAG=2023-05-01
FROM jupyter/base-notebook:${TAG}

USER root

ENV NOTEBOOK_VERSION 0.1.0

RUN groupadd -g 1026 climate && \
    usermod -a -G climate $NB_USER && \
    apt-get -q update && \
    DEBIAN_FRONTEND=noninteractive \
        apt-get install --yes --no-install-recommends \
        git less vim unzip rsync openssh-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir /notebooks

COPY notebooks/* /notebooks

USER $NB_USER
