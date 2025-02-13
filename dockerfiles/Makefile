.DEFAULT_GOAL: build

NAMESPACE ?= ghcr.io/esgf-nimbus

release build push run readme: REPOSITORY = $(lastword $(subst /, ,$(PWD)))

release: bump-patch changelog readme commit build push

build:
	docker build $(ARGS) -t $(NAMESPACE)/$(REPOSITORY):$(VERSION) . $(if $(POST_BUILD),&& $(POST_BUILD),)

push:
	docker push $(NAMESPACE)/$(REPOSITORY):$(VERSION)

run:
	docker run -it $(ARGS) -v $(PWD):/host $(if $(ENTRYPOINT),--entrypoint $(ENTRYPOINT),) $(NAMESPACE)/$(REPOSITORY):$(VERSION) $(COMMAND)

changelog:
	git log --pretty="%s [%h](https://github.com/esgf-nimbus/nimbus/commit/%h) (%cs)" . | python3 -c "import sys;lines=[f'- {x}' if x.startswith('Bump') else f'  - {x}' for x in sys.stdin]; print(''.join(['# Changelog\n'] + lines))" > changelog.md

bump-%:
	tbump --no-tag --no-push $(shell pysemver bump $* $(shell tbump current-version))

commit:
	git add .
	git commit -m "Updates $(REPOSITORY) to $(VERSION)"

readme:
	docker run -it --rm --entrypoint python -v $(PWD)/../:/host -w /host $(NAMESPACE)/$(REPOSITORY):$(VERSION) /host/generate.py $(REPOSITORY)/$(ENVIRONMENT_FILE) $(REPOSITORY)
