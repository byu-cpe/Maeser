# Minimal makefile for development setup

.PHONY: setup test testVerbose clean_venv

PYTHON := python3
VENV := .venv
PIP := $(VENV)/bin/pip
POETRY := $(VENV)/bin/poetry
PYTEST := $(VENV)/bin/pytest

setup: $(VENV)/bin/activate
	$(PIP) install poetry
	$(PIP) install langchain
	$(PIP) install tiktoken
	$(PIP) install PyMuPDF
	$(PIP) install Pillow
	$(PIP) install discord
	@echo "Updating poetry lock file if necessary..."
	$(POETRY) lock
	$(POETRY) install
	$(PIP) install -e .
	@echo "Maeser setup complete. Running pytests..."
	. $(VENV)/bin/activate && pytest tests

clean_venv:
	@echo "Removing existing virtual environment if it exists..."
	rm -rf $(VENV)

$(VENV)/bin/activate:
	@echo "Creating virtual environment in $(VENV)..."
	$(PYTHON) -m venv $(VENV)

test:
	@echo "Running tests..."
	$(PYTEST) tests

testVerbose:
	@echo "Running tests in verbose mode..."
	$(PYTEST) -v tests
