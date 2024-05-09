ARG TAG=2024-05-05

FROM quay.io/jupyter/base-notebook:${TAG}

LABEL org.opencontainers.image.source="https://github.com/esgf-nimbus/nimbus"
LABEL org.opencontainers.image.url="https://github.com/esgf-nimbus/nimbus/blob/main/dockerfiles/minimal-notebook/Dockerfile"

USER root

RUN groupadd -g 1026 climate && \
    usermod -a -G climate $NB_USER && \
    apt-get -q update && \
    DEBIAN_FRONTEND=noninteractive \
        apt-get install --yes --no-install-recommends \
        less \
        zip \
        unzip \
        lz4 \
        gzip \
        bzip2 \
        openssh-client \
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

RUN rm /opt/conda/conda-meta/pinned && \
    mamba install -y \
    "python<3.11" \
    zstandard \
    git \
    vim \
    rsync \
    curl && \
    rm -rf /opt/conda/pkgs

COPY scripts /scripts
COPY notebooks /notebooks
COPY changelog.md /changelog.md

RUN source /scripts/render-intro.sh && \
    chown -R $NB_USER:$NB_GROUP /home/jovyan

USER $NB_USER

ENTRYPOINT ["/scripts/entrypoint.sh"]
