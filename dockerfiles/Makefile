.PHONY: new-template
new-template: check-env
	cp -rf template/ $(NAME)

.PHONY: check-env
check-env:
ifndef NAME
	$(error NAME is undefined)
endif
