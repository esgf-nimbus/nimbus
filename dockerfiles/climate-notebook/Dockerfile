ARG TAG=0.1.19
FROM python:3.10 as intake-es-builder

COPY intake_es /intake_es

WORKDIR /intake_es

RUN pip install setuptools build && \
    python -m build

FROM ghcr.io/esgf-nimbus/minimal-notebook:${TAG}

LABEL org.opencontainers.image.source="https://github.com/esgf-nimbus/nimbus"
LABEL org.opencontainers.image.url="https://github.com/esgf-nimbus/nimbus/blob/main/dockerfiles/climate-notebook/Dockerfile"

USER root

COPY base.yaml /base.yaml

RUN --mount=type=cache,target=/opt/conda/pkgs \
    mamba env update -n base -f /base.yaml && \
    rm /base.yaml && \
    pip install ecoport && \
    python -m ecoport -f /base.yaml

COPY --from=intake-es-builder /intake_es/dist /build

RUN python -m pip install /build/*.tar.gz && \
    rm -rf /build

COPY scripts /scripts
COPY notebooks /notebooks
COPY changelog.md /changelog.md

RUN source /scripts/render-intro.sh

USER $NB_USER

ENTRYPOINT ["/scripts/entrypoint.sh"]
