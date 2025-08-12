# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This is the Maeser package, which provides a set of classes and
functions for managing a chat application.

The package is organized as follows:

:maeser.chat: This module contains classes and functions related to chat functionality, such as sending and receiving messages.
:maeser.controllers: This module contains classes and functions for managing Flask controllers, which handle the logic for handling incoming requests.
:maeser.graphs: This package contains Retrieval-Augmented Generation (RAG) graphs that affect the workflow and behavior of the chatbot.
:maeser.blueprints: This module sets up the Flask blueprint and associated routes for the Maeser application.
:maeser.user_manager: This module contains classes and functions for managing users in the chat application.
:maeser.render: This module contains classes and functions for rendering the user interface of the chat application.
"""

from . import (
    chat,
    controllers,
    graphs,
    blueprints,
    user_manager,
    render,
)

__all__ = [
    'chat',
    'controllers',
    'graphs',
    'blueprints',
    'user_manager',
    'render'
]
