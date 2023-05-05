HUB_REPO ?= jasonb87

SHELL ?= bash

# Rules to be called from dockerfile directory
# e.g. cd dockerfiles/minimal-notebook; make build-minimal-notebook
build-%:
	docker build -t $(HUB_REPO)/$*:$(VERSION) .

push-%:
	docker push $(HUB_REPO)/$*:$(VERSION)

run-%:
	docker run -it $(RUN_ARGS) --entrypoint $(SHELL) $(HUB_REPO)/$*:$(VERSION) 
