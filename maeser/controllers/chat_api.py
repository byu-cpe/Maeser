"""Module for handling chat API requests.

This module contains the controller function for managing chat sessions and processing incoming messages.
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
    # print("chat_api.controller response:",response)
    # print("response text:",response['messages'][-1])
    html_response = get_response_html(response['messages'][-1])
    return {'response': html_response, 'index': len(response['messages']) - 1}
