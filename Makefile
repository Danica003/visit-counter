-include .env
HOST_PORT ?= 8080

.PHONY: build up down test logs healthcheck

build:
	docker compose build

up:
	docker compose up -d --build

down:
	docker compose down

test:
	ruff check .
	pytest

logs:
	docker compose logs -f app

healthcheck:
	./scripts/healthcheck.sh http://localhost:$(HOST_PORT)