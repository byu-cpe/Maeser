"""Module for handling chat API requests.

This module contains the controller function for managing chat sessions and processing incoming messages.

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
from maeser.render import get_response_html
from flask import request, abort
from openai import RateLimitError

def controller(chat_sessions_manager: ChatSessionManager, chat_session: str):
    """Handle incoming messages for a chat session.

    Args:
        chat_sessions_manager (ChatSessionManager): The manager for chat sessions.
        chat_session (str): Chat session ID.

    Returns:
        dict: Response containing the HTML representation of the response.
    """
    posty = request.get_json()

    try:
        response = chat_sessions_manager.ask_question(posty['message'], posty['action'], chat_session)
    except RateLimitError as e:
        print(f'{type(e)}, {e}: Rate limit reached')
        abort(503, description='Rate limit reached, please try again later')
    
    return {'response': get_response_html(response['messages'][-1]), 'index': len(response['messages']) - 1}
