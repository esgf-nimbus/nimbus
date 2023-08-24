ARG TAG=2023-05-01
FROM python:3.10 as intake-es-builder

COPY intake_es /intake_es

WORKDIR /intake_es

RUN pip install setuptools build && \
    python -m build

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
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install nbgitpuller && \
    mkdir /notebooks

RUN --mount=type=cache,target=/opt/conda/pkgs \
    mamba install -y \
        xcdat \
        xarray \
        xarray-datatree \
        pandas \
        xesmf \
        xgcm \
        netcdf4 \
        s3fs \
        zarr \
        intake \
        intake-esm \
        intake-stac \
        intake-xarray \
        flox \
        holoviews \
        hvplot \
        datashader \
        seaborn \
        cartopy \
        matplotlib \
        nc-time-axis \
        ipywidgets \
        dask-gateway \
        'bokeh<3' && \
    conda env export -n base -f /base.yaml

COPY --from=intake-es-builder /intake_es/dist /build

RUN python -m pip install /build/*.tar.gz && \
    rm -rf /build

COPY scripts /scripts
COPY notebooks /notebooks
COPY changelog.md /changelog.md

RUN source /scripts/render-intro.sh

USER $NB_USER
