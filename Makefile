default: test

format:
	ruff check --fix .
	ruff format .

lint: format
	python -m isort .
	python -m ruff check .
	python -m ruff format --check .

test: lint
	# pytest .

run-app:
	streamlit run app.py

help: ## Show this help
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'
