ARG TAG=0.1.14
FROM ghcr.io/esgf-nimbus/minimal-notebook:${TAG}

USER root

RUN --mount=type=cache,target=/opt/conda/pkgs \
	mamba install -y \
	rapids \
	cupy && \
	chown -R ${NB_UID}:${NB_GID} /home/jovyan

COPY changelog.md /changelog.md

RUN source /scripts/render-intro.sh

USER $NB_USER
