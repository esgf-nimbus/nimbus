.PHONY: export-dask-gateway-env
export-dask-gateway-env:
	docker run -it \
		-u root:root \
		-v ./dockerfiles/minimal-notebook/conda-envs:/conda-envs \
		ghcr.io/esgf-nimbus/dask-gateway:$(shell tbump -C dockerfiles/dask-gateway current-version) \
		mamba env export -n base -f /conda-envs/dask-gateway.yaml
