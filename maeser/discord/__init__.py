# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This is the discord subpackage for the Maeser package.

This package provides a handler for interfacing Maeser with the discord API.
"""

from ._discord_handler import run_discord_handler as run_discord_handler

__all__ = ["run_discord_handler"]
