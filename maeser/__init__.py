# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This is the Maeser package, which provides a set of classes and
functions for managing a chat application.

The following modules and subpackages are included with Maeser by default:

:maeser.chat: This subpackage contains classes and functions related to chat functionality, such as
    sending and receiving messages.
:maeser.controllers: This subpackage contains classes and functions for managing Flask controllers,
    which handle the logic for handling incoming requests.
:maeser.graphs: This subpackage contains Retrieval-Augmented Generation (RAG) graphs that affect the
    workflow and behavior of the chatbot.
:maeser.flask_app: This module integrates Maeser with Flask, setting up the Flask blueprint and associated
    routes for the Maeser application.
:maeser.config: This module reads in `config.yaml` from the working directory and exposes its fields to
    other modules in the package.
:maeser.generate_response: This module provides a function named **handle_message** which handles branch
    registration and session management behind the scenes, simplifying the interface with Maeser.
:maeser.render: This module contains classes and functions for rendering the user interface of the chat application.
:maeser.user_manager: This module contains classes and functions for managing users in the chat application.

The following subpackages are optional and require additional dependencies:

:maeser.admin_portal: This subpackage provides access to the **Admin Portal**, a web applet that is useful
    for automatically vectorizing data and creating courses for use with other Maeser handlers, such as
    **maeser.discord_handler**. Requires the ``maeser[admin_portal]`` dependency group
    (`pip install maeser[admin_portal]`).
:maeser.discord_handler: This subpackage integrates Maeser with Discord. Requires the ``maeser[discord]``
    dependency group (`pip install maeser[discord]`).
"""

from . import (
    chat,
    controllers,
    flask_app,
    graphs,
    config,
    generate_response,
    user_manager,
    render,
    # Keep optional modules/packages commented out
    # admin_portal,
    # discord_handler,
)

__all__ = [
    "chat",
    "controllers",
    "flask_app",
    "graphs",
    "config",
    "generate_response",
    "user_manager",
    "render",
    # Keep optional modules/packages commented out
    # "admin_portal",
    # "discord_handler",
]
