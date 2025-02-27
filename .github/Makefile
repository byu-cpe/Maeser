# © 2024 Blaine Freestone

# This file is part of the Maeser unit test suite.

# Maeser is free software: you can redistribute it and/or modify it under the terms of
# the GNU Lesser General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# Maeser is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# Maeser. If not, see <https://www.gnu.org/licenses/>.

SHELL := /bin/bash
IN_ENV := source .venv/bin/activate;

env:
	@echo "Creating virtual environment..."
	python3 -m venv .venv
	$(IN_ENV) pip install setuptools packaging
	@echo "Virtual environment setup complete."

check_version_increase:
	@echo "Starting version check process..."

	@echo "Uninstalling existing Maeser package (if any)..."
	$(IN_ENV) pip uninstall -y maeser

	@echo "Installing Maeser from PyPI..."
	$(IN_ENV) pip install maeser

	@echo "Fetching installed Maeser version from PyPI..."
	$(IN_ENV) python print_version.py > pypi_version.txt

	@echo "PyPI version extracted: "
	@cat pypi_version.txt || echo "Error: pypi_version.txt is empty!"

	@echo "Uninstalling Maeser (PyPI version)..."
	$(IN_ENV) pip uninstall -y maeser

	@echo "Building and installing local version of Maeser..."
	$(IN_ENV) pip install ../dist/maeser-*.tar.gz

	@echo "Fetching installed local Maeser version..."
	$(IN_ENV) python print_version.py > current_version.txt

	@echo "Local version extracted: "
	@cat current_version.txt || echo "Error: current_version.txt is empty!"

	@echo "Uninstalling local Maeser package..."
	$(IN_ENV) pip uninstall -y maeser

	@echo "Comparing versions..."
	$(IN_ENV) python compare_versions.py pypi_version.txt current_version.txt

	@echo "Version check completed successfully."
