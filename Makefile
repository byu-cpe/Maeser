# Minimal makefile for development setup
# 2024 Carson Bush

# This file is part of the Maeser unit test suite.

# Maeser is free software: you can redistribute it and/or modify it under the terms of
# the GNU Lesser General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# Maeser is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# Maeser. If not, see <https://www.gnu.org/licenses/>.

# You can set these variables from the command line, and also
# from the environment for the first two.


.PHONY: setup test

PIP := pip
POETRY := poetry

setup:
	$(PIP) install -e .
	$(PIP) install poetry
	@echo "Updating poetry lock file if necessary..."
	$(POETRY) lock --no-update
	$(POETRY) install
	pytest tests

test:
	@echo "Running tests..."
	pytest tests

testVerbose:
	@echo "Running tests in verbose mode..."
	pytest -v tests
