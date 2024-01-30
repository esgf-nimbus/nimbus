.DEFAULT_GOAL = build

VERSION = 0.1.18

run: ARGS = -p 8888:8888 -v $(PWD)/../dask-gateway/conda-envs:/conda-envs

build: POST_BUILD = make export-env

.PHONY: export-env
export-env: ENTRYPOINT = /bin/bash
export-env: COMMAND = -c "cp /base.yaml /conda-envs/"
export-env: run

include ../Makefile
