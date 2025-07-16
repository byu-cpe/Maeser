# SPDX-License-Identifier: LGPL-3.0-or-later

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
"""

from . import chat
from . import controllers
from . import user_manager
from . import render

__all__ = ['chat', 'controllers', 'user_manager', 'render']
