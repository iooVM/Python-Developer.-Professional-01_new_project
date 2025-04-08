
### Makefile

```makefile
.PHONY: lint test run

lint:
	poetry run flake8 log_analyzer tests
	poetry run black --check log_analyzer tests
	poetry run isort --check-only log_analyzer tests
	poetry run mypy log_analyzer tests

test:
	poetry run pytest -v

run:
	poetry run python -m log_analyzer