"""
This is the chat subpackage for the Maeser package.

This package contains the following subpackages and modules:

- `chat_logs`: This module provides functionality for managing chat logs.
- `chat_session_manager`: This module provides functionality for managing chat sessions.

© 2024 Carson Bush, Blaine Freestone

This file is part of Maeser.

Maeser is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

Maeser is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with
Maeser. If not, see <https://www.gnu.org/licenses/>.
"""

from . import chat_logs
from . import chat_session_manager

__all__ = ["chat_logs", "chat_session_manager"]