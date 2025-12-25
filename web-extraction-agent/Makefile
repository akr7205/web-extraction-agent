# Makefile for Web Extractor Agent

.PHONY: help install install-dev test test-cov lint format clean run-api run-cli docs

help:
	@echo "Web Extractor Agent - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make install       - Install production dependencies"
	@echo "  make install-dev   - Install development dependencies"
	@echo "  make test          - Run tests"
	@echo "  make test-cov      - Run tests with coverage report"
	@echo "  make lint          - Run linters (flake8, mypy)"
	@echo "  make format        - Format code (black, isort)"
	@echo "  make clean         - Remove generated files"
	@echo "  make run-api       - Start API server"
	@echo "  make run-cli       - Run interactive CLI"
	@echo "  make examples      - Run all examples"
	@echo ""

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -e ".[dev]"

test:
	pytest tests/

test-cov:
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

lint:
	flake8 src tests --max-line-length=100
	mypy src --ignore-missing-imports

format:
	black src tests examples --line-length=100
	isort src tests examples --profile black

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build dist .pytest_cache .coverage htmlcov
	rm -rf extraction_result*.json site_extraction*.json

run-api:
	cd src && uvicorn app:app --reload

run-cli:
	python cli_keyword_extract.py

examples:
	@echo "Running Example 1: Basic Extraction"
	python examples/01_basic_extraction.py
	@echo ""
	@echo "Running Example 3: Site-Wide Extraction"
	python examples/03_site_wide_extraction.py
	@echo ""
	@echo "Running Example 4: Library Usage"
	python examples/04_library_usage.py

build:
	python setup.py sdist bdist_wheel

upload-test:
	python -m twine upload --repository testpypi dist/*

upload:
	python -m twine upload dist/*
