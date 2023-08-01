.DEFAULT_GOAL = build

VERSION = 0.1.0

.PHONY: env-export
env-export: ARGS = -v $(PWD)/../minimal-notebook/conda-envs:/conda-envs
env-export: ENTRYPOINT = /bin/bash
env-export: COMMAND = -c "conda env export -f /conda-envs/dask-gateway.yaml"
env-export: run

include ../Makefile
