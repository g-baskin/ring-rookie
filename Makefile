.PHONY: help install dev stop clean reset-database test lint format migrate check backend-ci frontend-ci migration-check security-check dependency-check env-check ci
help:
	@echo "CI: backend-ci frontend-ci migration-check security-check dependency-check env-check ci"
	@echo "Maintenance: clean (artifacts only), reset-database CONFIRM_RESET=yes (destructive)"
install:
	cd backend && uv sync --all-extras
	cd frontend && npm ci
dev:
	docker compose up -d postgres redis
stop:
	docker compose down
clean:
	rm -rf backend/.mypy_cache backend/.pytest_cache backend/.ruff_cache frontend/.next frontend/coverage
reset-database:
	@test "$(CONFIRM_RESET)" = yes || (echo "Destructive: rerun with CONFIRM_RESET=yes"; exit 1)
	docker compose down -v
test:
	cd backend && uv run pytest
	cd frontend && npm test
lint:
	cd backend && uv run ruff check app tests && uv run mypy app
	cd frontend && npm run lint
format:
	cd backend && uv run ruff format app tests
	cd frontend && npm run format
migrate:
	cd backend && uv run alembic upgrade head
backend-ci:
	cd backend && uv sync --frozen --all-extras
	cd backend && uv run ruff check app tests && uv run ruff format --check app tests && uv run mypy app
	cd backend && uv run pytest --cov-fail-under=60
frontend-ci:
	cd frontend && npm ci && npm run lint && npm run type-check && npm run format:check && npm test && npm run build
migration-check:
	@test "$$(cd backend && uv run alembic heads | grep -c '(head)')" = 1
	cd backend && uv run alembic upgrade head && uv run alembic check
	cd backend && uv run alembic downgrade -1 && uv run alembic upgrade head
security-check:
	gitleaks detect --redact --no-banner
dependency-check:
	@mkdir -p .audit
	@cd backend && uv export --frozen --no-dev --no-emit-project | uvx --python 3.12 pip-audit -r /dev/stdin --disable-pip --no-deps --format json --output ../.audit/python.json || test -s ../.audit/python.json
	@cd frontend && npm audit --omit=dev --audit-level=high --json > ../.audit/npm.json || test -s ../.audit/npm.json
	@python3 scripts/check_dependency_audit.py --python-report .audit/python.json --npm-report .audit/npm.json
	@rm -rf .audit
env-check:
	python3 scripts/check_env_drift.py
check: backend-ci frontend-ci env-check
ci: backend-ci frontend-ci migration-check security-check dependency-check env-check
