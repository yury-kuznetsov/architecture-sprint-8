SHELL=/bin/bash
## or docker compose
DCC=docker-compose

up: ## Run containers
	$(DCC) up -d

down: ## Down containers
	$(DCC) down

build: ## Build containers
	$(DCC) build

run: down build up