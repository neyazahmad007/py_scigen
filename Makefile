# Makefile for SCIgen-py

.PHONY: help install install-dev test lint format type-check clean docs docker

help:  ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package
	pip install -e .

install-dev:  ## Install with development dependencies
	pip install -e ".[dev]"
	pre-commit install

test:  ## Run tests
	pytest -v

test-cov:  ## Run tests with coverage
	pytest --cov=scigen --cov-report=html --cov-report=term

test-fast:  ## Run tests excluding slow ones
	pytest -v -m "not slow"

lint:  ## Run all linters
	ruff check src/ tests/
	pylint src/scigen

format:  ## Format code
	black src/ tests/ examples/
	isort src/ tests/ examples/

type-check:  ## Run type checking
	mypy src/

check:  ## Run all checks (lint + type-check + test)
	make lint
	make type-check
	make test

clean:  ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf htmlcov/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs:  ## Build documentation
	cd docs && make html

docker-build:  ## Build Docker image
	docker build -t scigen-py .

docker-run:  ## Run in Docker
	docker run -it -v $$(pwd)/output:/output scigen-py

example-paper:  ## Generate example paper
	python examples/generate_paper.py

example-grammar:  ## Run grammar examples
	python examples/grammar_basics.py

benchmark:  ## Run performance benchmarks
	pytest tests/ -v --benchmark-only

pre-commit:  ## Run pre-commit on all files
	pre-commit run --all-files

publish-test:  ## Publish to Test PyPI
	python -m build
	twine upload --repository testpypi dist/*

publish:  ## Publish to PyPI
	python -m build
	twine upload dist/*
