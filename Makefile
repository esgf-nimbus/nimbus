HUB_REPO ?= jasonb87

# Rules to be called from dockerfile directory
# e.g. cd dockerfiles/minimal-notebook; make build-minimal-notebook
build-%:
	docker build -t $(HUB_REPO)/$*:$(VERSION) .

push-%:
	docker push -t $(HUB_REPO)/$*:$(VERSION)
