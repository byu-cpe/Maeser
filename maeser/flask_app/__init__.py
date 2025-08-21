# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This is the flask subpackage for the Maeser package.

This package contains the following modules:

:blueprints: sets up the **Flask blueprint** and associated routes for a Maeser Flask application.
"""

from maeser._utils.pkg_utils import autoimport_all
import sys

__all__ = autoimport_all(sys.modules[__name__], include_packages=True)
