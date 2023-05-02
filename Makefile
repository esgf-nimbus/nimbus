HUB_REPO ?= jasonb87

MINIMAL_NOTEBOOK_TAG := 0.1.0


.PHONY: build-minimal-notebook
build-minimal-notebook:
	docker build -t $(HUB_REPO)/minimal-notebook:$(MINIMAL_NOTEBOOK_TAG) dockerfiles/minimal-notebook

.PHONY: push-minimal-notebook
push-minimal-notebook:
	docker push $(HUB_REPO)/minimal-notebook:$(MINIMAL_NOTEBOOK_TAG)
