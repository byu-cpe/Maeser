"""
© 2024 Blaine Freestone

This file is part of the Maeser GitHub actions.

Maeser is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

Maeser is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with
Maeser. If not, see <https://www.gnu.org/licenses/>.
"""

import sys
from packaging import version

pypi_version_path = sys.argv[1]
this_version_path = sys.argv[2]

pypi_version = version.parse(open(pypi_version_path).read())
this_version = version.parse(open(this_version_path).read())

if this_version <= pypi_version:
    raise Exception(
        f"This version ({this_version}) is not greater than the pypi version ({pypi_version})"
    )