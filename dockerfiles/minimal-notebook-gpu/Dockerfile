ARG TAG
FROM ghcr.io/esgf-nimbus/minimal-notebook:${TAG}

USER root

RUN --mount=type=cache,target=/opt/conda/pkgs \
	mamba install -y \
	rapids \
	cupy && \
	chown -R ${NB_UID}:${NB_GID} /home/jovyan

USER $NB_USER
