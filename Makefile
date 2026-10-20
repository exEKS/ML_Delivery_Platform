.PHONY: bootstrap format format-check lint typecheck test-unit check fix

bootstrap:
	uv sync --all-packages

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

lint:
	uv run ruff check .

typecheck:
	uv run mypy packages/platform_contracts/src/platform_contracts packages/platform_contracts/tests examples/credit_default

test-unit:
	uv run python -m pytest packages/platform_contracts/tests examples/credit_default/tests -q

check: lint format-check typecheck test-unit

fix:
	uv run ruff check . --fix
	uv run ruff format .