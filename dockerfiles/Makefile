.DEFAULT_GOAL: build

NAMESPACE ?= ghcr.io/esgf-nimbus

build push run: REPOSITORY = $(lastword $(subst /, ,$(PWD)))

build: changelog
	docker build $(ARGS) -t $(NAMESPACE)/$(REPOSITORY):$(VERSION) . && \
		$(POST_BUILD)

push:
	docker push $(NAMESPACE)/$(REPOSITORY):$(VERSION)

run:
	docker run -it $(ARGS) -v $(PWD):/host $(if $(ENTRYPOINT),--entrypoint $(ENTRYPOINT),) $(NAMESPACE)/$(REPOSITORY):$(VERSION) $(COMMAND)

changelog:
	git log --pretty="%s [%h](https://github.com/esgf-nimbus/nimbus/commit/%h) (%cs)" . | python -c "import sys;lines=[f'- {x}' if x.startswith('Bump') else f'  - {x}' for x in sys.stdin]; print(''.join(['# Changelog\n'] + lines))" > changelog.md

bump-%:
	tbump $(if $(COMMIT),,--dry-run) --no-tag --no-push $(shell pysemver bump $* $(shell tbump current-version)) $(if $(COMMIT),&& make changelog && git add changelog.md && git commit -m "Updates changelog",)
