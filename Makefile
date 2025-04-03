.PHONY: help test update_repo

help: ## Display this help message
	@echo "Please use \`make <target>\` where <target> is one of:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; \
	{printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}'

update_repo: ## Updates git repository
	git pull --recurse-submodules=yes
	git submodule update --remote --merge --recursive --init

test: ## Run tests
	py.test -vv .