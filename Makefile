# Minimal makefile for development setup
# 2025 Gohaun Manley

# This file is part of the Maeser unit test suite.

# Maeser is free software: you can redistribute it and/or modify it under the terms of
# the GNU Lesser General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# Maeser is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# Maeser. If not, see <https://www.gnu.org/licenses/>.

.PHONY: setup test testVerbose clean_venv

PYTHON := python3
VENV := .venv
PIP := $(VENV)/bin/pip
POETRY := $(VENV)/bin/poetry
PYTEST := $(VENV)/bin/pytest

setup: $(VENV)/bin/activate
	$(PIP) install poetry
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
