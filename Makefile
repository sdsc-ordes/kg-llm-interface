
.PHONY: install
install: ## Install with the poetry and add pre-commit hooks
	@echo "🚀 Installing packages with poetry"
	@poetry install
	@poetry run pre-commit install

.PHONY: check
check: ## Run code quality tools.
	@echo "🚀 Checking Poetry lock file consistency with 'pyproject.toml': Running poetry lock --check"
	@poetry lock --check
	@echo "🚀 Linting code: Running pre-commit"
	@poetry run pre-commit run -a

.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@CHROMA_HOST=${CHROMA_HOST} CHROMA_PORT=${CHROMA_PORT} SPARQL_ENDPOINT=http://${SPARQL_HOST}:${SPARQL_PORT}/repositories/test poetry run pytest

.PHONY: deploy
deploy:
	@echo "🚀 Deploying all the services"
	@kubectl apply -k kubernetes/overlays/data-retriever

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
