# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This is the admin_portal subpackage for the Maeser package.

The **run_admin_portal()** function provides access to the **Admin Portal**, a web applet that is
useful for automatically vectorizing data and creating courses for use with other Maeser handlers,
such as **maeser.discord_handler**.

In order to use this subpackage, the dependencies in `maeser[admin_portal]` must be installed
(`pip install maeser[admin_portal]`).
"""

from maeser._utils.pkg_utils import autoimport_all
import sys

from ._flask_admin_portal import run_admin_portal as run_admin_portal

__all__ = autoimport_all(sys.modules[__name__], include_packages=True)
__all__ += [
    "run_admin_portal",
]
