.DEFAULT_GOAL: build

NAMESPACE ?= ghcr.io/esgf-nimbus

build push run: REPOSITORY = $(lastword $(subst /, ,$(PWD)))

build:
	docker build -t $(NAMESPACE)/$(REPOSITORY):$(VERSION) .

push:
	docker push $(NAMESPACE)/$(REPOSITORY):$(VERSION)

run:
	docker run -it $(RUN_ARGS) $(if $(ENTRYPOINT),--entrypoint $(ENTRYPOINT),) $(NAMESPACE)/$(REPOSITORY):$(VERSION) 
