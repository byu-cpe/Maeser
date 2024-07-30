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

IN_ENV := . .venv/bin/activate;

env:
	python3 -m venv .venv
	$(IN_ENV) pip install packaging

check_version_increase:
	$(IN_ENV) pip uninstall -y maeser
	$(IN_ENV) pip install maeser
	$(IN_ENV) echo `python print_version.py` > pypi_version.txt
	$(IN_ENV) pip uninstall -y maeser
	$(IN_ENV) pip install ../dist/maeser*.tar.gz
	$(IN_ENV) echo `python print_version.py` > current_version.txt
	$(IN_ENV) pip uninstall -y maeser
	$(IN_ENV) python compare_versions.py pypi_version.txt current_version.txt