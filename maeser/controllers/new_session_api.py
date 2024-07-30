"""
This module handles API requests for creating new chat sessions.

It uses the ChatSessionManager to manage session creation and optionally integrates
with user management through Flask-Login's current_user.

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

from maeser.chat.chat_session_manager import ChatSessionManager
from flask import request
from flask_login import current_user

def controller(session_handler: ChatSessionManager, user_management: bool = False):
    """
    Handle session requests.

    Args:
        session_handler (ChatSessionManager): The session handler instance.
        user_management (bool): Flag to indicate if user management is enabled.

    Returns:
        dict: Response confirming session action or an error message.
    """
    posty = request.get_json()
    branch_action = posty['action']
    if posty['type'] == 'new':
        if user_management:
            return {'response': session_handler.get_new_session_id(branch_action, current_user)} # type: ignore
        return {'response': session_handler.get_new_session_id(branch_action)}
    return {'response': 'invalid', 'details': 'Requested session type is not valid'}
