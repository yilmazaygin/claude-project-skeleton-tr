local = docker compose -f compose.local.yaml
live = docker compose -f compose.live.yaml

.PHONY: up down live-up live-down

up:
	$(local) up -d

down:
	$(local) down

live-up:
	$(live) up -d

live-down:
	$(live) down
