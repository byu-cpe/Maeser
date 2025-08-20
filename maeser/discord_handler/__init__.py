# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This is the discord subpackage for the Maeser package.

The **run_discord_handler()** function provides a handler for interfacing Maeser with the discord API.

In order to use this subpackage, the dependencies in `maeser[discord]` must be installed
(`pip install maeser[discord]`).
"""

# Only export "run_discord_handler" to the package
from ._discord_handler import run_discord_handler as run_discord_handler

__all__ = ["run_discord_handler"]
