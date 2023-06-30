.DEFAULT_GOAL: build

NAMESPACE ?= jasonb87

CONTAINER_SHELL ?= /bin/bash

.PHONY: new-template
new-template: check-env
	cp -rf template/ $(NAME)

.PHONY: check-env
check-env:
ifndef NAME
	$(error NAME is undefined)
endif

build push run: REPOSITORY = $(lastword $(subst /, ,$(PWD)))

build:
	docker build -t $(NAMESPACE)/$(REPOSITORY):$(VERSION) .

push:
	docker push $(NAMESPACE)/$(REPOSITORY):$(VERSION)

run:
	docker run -it $(RUN_ARGS) --entrypoint $(CONTAINER_SHELL) $(NAMESPACE)/$(REPOSITORY):$(VERSION) 
