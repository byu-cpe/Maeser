# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This is the discord subpackage for the Maeser package.

This package provides a handler for interfacing Maeser with the discord API.
"""

from maeser._utils.pkg_utils import autoimport_all
import sys

from maeser.discord.discord_handler import run_discord_handler

__all__ = ["run_discord_handler"]
__all__ += autoimport_all(sys.modules[__name__], include_packages=True)
