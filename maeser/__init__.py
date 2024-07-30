"""
This is the Maeser package, which provides a set of classes and
functions for managing a chat application.

The package is organized as follows:

- `chat`: This module contains classes and functions related to chat functionality,
          such as sending and receiving messages.
- `controllers`: This module contains classes and functions for managing Flask
          controllers, which handle the logic for handling incoming requests.
- `user_manager`: This module contains classes and functions for managing users
          in the chat application.
- `render`: This module contains classes and functions for rendering the user
          interface of the chat application.

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

from . import chat
from . import controllers
from . import user_manager
from . import render

__all__ = ['chat', 'controllers', 'user_manager', 'render']
