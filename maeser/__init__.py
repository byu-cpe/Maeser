# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This is the Maeser package, which provides a set of classes and
functions for managing a chat application.

The package is organized as follows:

:maeser.chat: This subpackage contains classes and functions related to chat functionality, such as
    sending and receiving messages.
:maeser.controllers: This subpackage contains classes and functions for managing Flask controllers,
    which handle the logic for handling incoming requests.
:maeser.discord_handler: This subpackage integrates Maeser with Discord.
:maeser.graphs: This subpackage contains Retrieval-Augmented Generation (RAG) graphs that affect the
    workflow and behavior of the chatbot.
:maeser.blueprints: This module sets up the Flask blueprint and associated routes for the Maeser application.
:maeser.config: This module reads in `config.yaml` from the working directory and exposes its fields to
    other modules in the package.
:maeser.generate_response: This module provides a function named **handle_message** which handles branch
    registration and session management behind the scenes, simplifying the interface with Maeser.
:maeser.render: This module contains classes and functions for rendering the user interface of the chat application.
:maeser.user_manager: This module contains classes and functions for managing users in the chat application.
"""

from . import (
    chat,
    controllers,
    discord_handler,
    graphs,
    blueprints,
    config,
    generate_response,
    user_manager,
    render,
)

__all__ = [
    'chat',
    'controllers',
    'discord_handler',
    'graphs',
    'blueprints',
    'config',
    'generate_response',
    'user_manager',
    'render'
]
