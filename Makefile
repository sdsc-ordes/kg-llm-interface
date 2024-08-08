IMAGE := 'ghcr.io/sdsc-ordes/kg-llm-interface:latest'

.PHONY: install
install: ## Install with the poetry and add pre-commit hooks
	@echo "🔨 Installing packages with poetry"
	@poetry install
	@poetry run pre-commit install

.PHONY: check
check: ## Run code quality tools.
	@echo "🕵️ Checking Poetry lock file consistency with 'pyproject.toml': Running poetry lock --check"
	@poetry lock --check
	@echo "🕵️ Linting code: Running pre-commit"
	@poetry run pre-commit run -a

.PHONY: test
test: ## Test the code with pytest
	@echo "🧪 Testing code: Running pytest"
	@poetry run pytest

.PHONY: server
server:
	@echo "🖥️ Running server"
	@poetry run uvicorn --reload aikg.server:app --port 8001

.PHONY: deploy
deploy:
	@echo "🚀 Deploying all the services"
	@kubectl apply -k kubernetes/overlays/data-retriever

.PHONY: notebook
notebook: docker-build ## Start a jupyter notebook server in a docker container
	@echo "🗒️ Starting a containerized notebook server"
	@docker run -p 8888:8888 --rm -it --entrypoint 'poetry' $(IMAGE) \
		run jupyter lab --allow-root --port 8888 --ip "0.0.0.0"

docker-build: Dockerfile
	@echo "🐳 Building docker image"
	@docker build -t $(IMAGE) .

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
