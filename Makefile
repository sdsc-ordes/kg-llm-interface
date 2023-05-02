TEST_SCHEMA=https://www.pokemonkg.org/ontology/ontology.nt
TEST_INSTANCES=https://www.pokemonkg.org/download/dump/poke-a.nq.gz

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
	@poetry run pytest

.PHONY: run
test-run: ## Run metaflow pipeline
	@echo "Test run of metaflow pipeline"
	@curl $(TEST_INSTANCES) -o - \
		| gzip -dc > /tmp/instances.nq
	@curl $(TEST_SCHEMA) -o /tmp/schema.nt
	@poetry run python aikg/pipeline/chroma_build.py run \
		--instance_path /tmp/instances.nq \
		--schema_path /tmp/schema.nt

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
