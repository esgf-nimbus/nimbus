ARG TAG=23.1.0-4
ARG IMAGE=condaforge/mambaforge
FROM ${IMAGE}:${TAG}

LABEL org.opencontainers.image.source="https://github.com/esgf-nimbus/nimbus"
LABEL org.opencontainers.image.url="https://github.com/esgf-nimbus/nimbus/blob/main/dockerfiles/dask-gateway/Dockerfile"

RUN groupadd --gid 1000 conda && \
	chown -R root:conda /opt && \
	chmod -R 0775  /opt && \
	useradd --create-home --user-group --uid 1000 dask && \
	usermod -a -G conda dask

USER dask:conda

WORKDIR /home/dask

COPY --chown=dask:conda conda-envs/ /conda-envs

RUN --mount=type=cache,target=/opt/conda/pkgs \
	mamba env update -n base -f /conda-envs/base.yaml && \
	mamba remove xesmf --force && \
	mamba install -y \
		tini

ENTRYPOINT ["tini", "-g", "--"]
