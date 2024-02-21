ARG TAG=0.1.0
ARG IMAGE=ghcr.io/esgf-nimbus/llnl-notebook
FROM ${IMAGE}:${TAG}

USER root

COPY base.yaml /base.yaml

RUN --mount=type=cache,target=/opt/conda/pkgs \
	mamba env update -n base -f /base.yaml && \
	rm /base.yaml && \
	chown -R ${NB_UID}:${NB_GID} /home/jovyan

COPY changelog.md /changelog.md

RUN source /scripts/render-intro.sh

USER $NB_USER
