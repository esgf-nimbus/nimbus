.DEFAULT_GOAL: build

NAMESPACE ?= ghcr.io/esgf-nimbus

build push run: REPOSITORY = $(lastword $(subst /, ,$(PWD)))

build: changelog
	docker build $(ARGS) -t $(NAMESPACE)/$(REPOSITORY):$(VERSION) .

push:
	docker push $(NAMESPACE)/$(REPOSITORY):$(VERSION)

run:
	docker run -it $(ARGS) -v $(PWD):/host $(if $(ENTRYPOINT),--entrypoint $(ENTRYPOINT),) $(NAMESPACE)/$(REPOSITORY):$(VERSION) $(COMMAND)

changelog:
	git log --pretty="%s [%h](https://github.com/esgf-nimbus/nimbus/commit/%h) (%cr)" . | python -c "import sys;lines=[f'- {x}' if 'Bump' in x else f'  - {x}' for x in sys.stdin]; print(''.join(['# Changelog\n'] + lines))" > changelog.md

bump-%:
	tbump $(if $(COMMIT),,--dry-run) --no-tag $(shell pysemver bump $* $(shell tbump current-version))
