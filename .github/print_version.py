# SPDX-License-Identifier: LGPL-3.0-or-later

import pkg_resources  # part of setuptools

version = pkg_resources.require("maeser")[0].version
print(version)