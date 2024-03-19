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
        zip \
        unzip \
        lz4 \
        gzip \
        bzip2 \
        rsync \
        openssh-client \
        curl \
        locate \
        htop \
        iputils-ping \
        dnsutils \
        texlive-full \
        && \
    apt-get purge && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install nbgitpuller && \
    mkdir /notebooks

COPY scripts /scripts
COPY notebooks /notebooks
COPY changelog.md /changelog.md

RUN source /scripts/render-intro.sh

USER $NB_USER

ENTRYPOINT ["/scripts/entrypoint.sh"]
