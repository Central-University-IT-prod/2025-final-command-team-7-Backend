lint: ruff-format ruff-check dmypy


ruff-format:
    uv run ruff format .

ruff-check:
    uv run ruff check --fix --unsafe-fixes --exit-zero .

mypy:
    uv run mypy . || true

dmypy:
    uv run dmypy run -- . || true

unit:
    uv run pytest tests/unit

integration:
    uv run pytest tests/integration

e2e:
    uv run pytest tests/e2e


dev:
    uv run litestar --app=backend.main.app:create_app run --reload --debug
