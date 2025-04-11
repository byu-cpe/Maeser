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

.PHONY: setup clean test testVerbose

PYTHON := python3
VENV_DIR := .venv
POETRY := poetry

setup: clean
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Activating virtual environment and installing dependencies..."
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install poetry
	$(POETRY) lock --no-update
	$(POETRY) install
	@echo "Installing project in editable mode..."
	$(VENV_DIR)/bin/pip install -e .
	@echo "Running initial tests..."
	tests tests

clean:
	@echo "Removing existing virtual environment (if any)..."
	rm -rf $(VENV_DIR)

test:
	@echo "Running tests..."
	tests tests

testVerbose:
	@echo "Running tests in verbose mode..."
	./tests -v tests
