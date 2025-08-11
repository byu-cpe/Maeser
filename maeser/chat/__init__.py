# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This is the chat subpackage for the Maeser package.

This package contains the following subpackages and modules:

:chat_logs: This module provides functionality for managing chat logs.
:chat_session_manager: This module provides functionality for managing chat sessions.
"""

from maeser._utils.pkg_utils import autoimport_all
import sys

__all__ = autoimport_all(sys.modules[__name__], include_packages=True)
