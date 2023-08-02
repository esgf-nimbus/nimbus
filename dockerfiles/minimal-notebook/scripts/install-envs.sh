#!/bin/bash

mamba env update -n base -f /conda-envs/dask-gateway.yaml

for env in $(find /conda-envs -type f -printf "%f\n"); do
	name="${env%.*}"
	mamba env create -n "${name}" -f "/conda-envs/${env}"
	source /opt/conda/etc/profile.d/conda.sh
	conda activate "${name}"
	python -m ipykernel install --name="${name}"
	conda deactivate
done
