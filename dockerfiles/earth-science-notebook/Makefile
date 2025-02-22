.DEFAULT_GOAL = build

VERSION = 0.1.6

release: POST_RELEASE = git add .; git commit -m "Updates dask-gateway environment"

run: ARGS = -p 8888:8888 -v $(PWD)/../dask-gateway/conda-envs:/conda-envs

build: ARGS = --build-arg="BUILD=$(shell date)"
build: POST_BUILD = make export-env

.PHONY: export-env
export-env: ENTRYPOINT = /bin/bash
export-env: COMMAND = -c "cp /base.yaml /conda-envs/"
export-env: run

ENVIRONMENT_FILE = base.yaml

include ../Makefile
