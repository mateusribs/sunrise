lint:
	@uv run --no-sync ruff check

format:
	@uv run --no-sync ruff check --fix
	@uv run --no-sync ruff format

test:
	@uv run --no-sync pytest -s -x --cov=src -vvv

run:
	@uv run --no-sync fastapi dev src/api.py

install:
	@uv sync --locked

upgrade_db:
	@uv run --no-sync alembic upgrade head

create_migration: upgrade_db
	@uv run --no-sync alembic revision --autogenerate -m "$(MIGRATION_NAME)"

run_docker:
	docker compose up --build