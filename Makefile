.PHONY: export-dask-gateway-env
export-dask-gateway-env:
	docker run -it \
		-u root:root \
		-v ./dockerfiles/minimal-notebook/conda-envs:/conda-envs \
		ghcr.io/esgf-nimbus/dask-gateway:$(shell tbump -C dockerfiles/dask-gateway current-version) \
		mamba env export -n base -f /conda-envs/dask-gateway.yaml

.PHONY: build-venv
build-venv:
	python3 -m venv build-venv
	. build-venv/bin/activate && \
		pip install tbump semver

.PHONY: release
release: 
	@for container in earth-science-notebook earth-science-notebook-gpu dask-gateway; do \
		cd dockerfiles/$$container; \
		make release; \
		cd ../..; \
	done
