"""Module for handling chat interface rendering.

This module contains a function to render the chat interface template with relevant data.
"""

from flask import render_template
# from flask_login import current_user

from .common.file_info import get_file_list
from maeser.chat.chat_session_manager import ChatSessionManager

def controller(
        chat_sessions_manager: ChatSessionManager,
        max_requests: int | None = None,
        rate_limit_interval: int | None = None,
        current_user=None,
        app_name: str | None = None,
        main_logo_light: str | None = None,
        main_logo_dark: str | None = None,
        chat_head: str | None = None,
        favicon: str | None = None,        
    ):
    """
    Renders the chat interface template with relevant data.

    Args:
        chat_sessions_manager (ChatSessionManager): The chat session manager object.
        max_requests (int, optional): The maximum number of requests a user can make. Defaults to None.
        rate_limit_interval (int, optional): The interval in seconds for rate limiting requests. Defaults to None.
        current_user (object, optional): The current user object. Defaults to None.

    Returns:
        The rendered 'chat_interface.html' template with the following data:
            - conversation: None (no active conversation)
            - buttons: The dictionary of available chat branches
            - links: A list of dictionaries representing previous chat sessions for the current user
            - requests_remaining: The number of requests remaining for the current user (10 if current_user is None)
            - max_requests_remaining: The maximum number of requests allowed
            - requests_remaining_interval_ms: The interval in milliseconds for rate limiting requests (rate_limit_interval * 1000 / 3)
    """
    # Get chat log path and branches from chat sessions
    log_path: str | None = chat_sessions_manager.chat_log_path
    chat_branches: dict = chat_sessions_manager.branches

    links = []
    # Get conversation history if log path exists
    if log_path:
        conversations = get_file_list(log_path + '/chat_history')
        for conversation in conversations:
            current_user_name: str = 'anon' if current_user is None else current_user.full_id_name
            if current_user_name == conversation['user']:
                links.append({
                    'branch': conversation['branch'],
                    'session': conversation['name'].removesuffix('.log'),
                    'modified': conversation['modified'],
                    'first_message': conversation['first_message']
                })
        # Sort conversations by date modified
        links.sort(key=lambda x: x['modified'], reverse=True)

    # Remove conversations with no messages
    links = [link for link in links if link['first_message'] is not None]
    requests_remaining: int | None = None if current_user is None else current_user.requests_remaining
    if rate_limit_interval:
        rate_limit_interval = rate_limit_interval * 1000 // 3
    rate_limiting_bool = bool(requests_remaining and rate_limit_interval and max_requests)
    rate_limiting_str: str = str(rate_limiting_bool).lower()

    return render_template(
        'chat_interface.html',
        conversation=None,
        buttons=chat_branches,                                  # dict
        links=links,                                            # List[dict]
        requests_remaining=requests_remaining,                  # None | int
        max_requests_remaining=max_requests,                    # None | int
        requests_remaining_interval_ms=rate_limit_interval,     # None | int
        rate_limiting=rate_limiting_str,                        # bool
        main_logo_light=main_logo_light,                        # None | str
        main_logo_dark=main_logo_dark,                          # None | str
        chat_head=chat_head,                                    # None | str
        favicon=favicon,                                        # None | str
        app_name=app_name if app_name else "Maeser",
    )
