ARG TAG=23.1.0-4
FROM condaforge/mambaforge:${TAG}

LABEL org.opencontainers.image.source="https://github.com/esgf-nimbus/nimbus"
LABEL org.opencontainers.image.url="https://github.com/esgf-nimbus/nimbus/blob/main/dockerfiles/dask-gateway/Dockerfile"

RUN groupadd --gid 1000 conda && \
	chown -R root:conda /opt && \
	chmod -R 0775  /opt && \
	useradd --create-home --user-group --uid 1000 dask && \
	usermod -a -G conda dask

USER dask:conda

WORKDIR /home/dask

RUN --mount=type=cache,target=/opt/conda/pkgs \
	mamba install -y \
		dask-gateway \
		tini \
		ipykernel \
		'bokeh<3' \
		xarray \
		netcdf4

ENTRYPOINT ["tini", "-g", "--"]
