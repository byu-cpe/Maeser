# SPDX-License-Identifier: LGPL-3.0-or-later

# Minimal makefile for development setup

.PHONY: setup test testVerbose clean_venv

PYTHON := python3
VENV := .venv
WITH_VENV := . $(VENV)/bin/activate &&
PIP := $(VENV)/bin/pip
POETRY := $(VENV)/bin/poetry
PYTEST := $(VENV)/bin/pytest

setup: $(VENV)/bin/activate
	$(PIP) install poetry
	@echo "Updating poetry lock file if necessary..."
	$(POETRY) lock
	$(POETRY) install --all-extras
	$(PIP) install -e .
	@echo "Maeser setup complete. Running pytests..."
	$(PYTEST) tests

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
