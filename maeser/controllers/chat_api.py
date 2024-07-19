"""Module for handling chat API requests.

This module contains the controller function for managing chat sessions and processing incoming messages.
"""

from maeser.chat.chat_session_manager import ChatSessionManager
from flask import request, abort
from openai import RateLimitError
from .common.render import get_response_html

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
