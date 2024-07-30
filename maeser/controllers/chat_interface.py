"""Module for handling chat interface rendering.

This module contains a function to render the chat interface template with relevant data.

© 2024 Blaine Freestone, Carson Bush

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

from flask import render_template

from maeser.chat.chat_logs import BaseChatLogsManager
# from flask_login import current_user

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
    log_manager: BaseChatLogsManager | None = chat_sessions_manager.chat_logs_manager
    chat_branches: dict = chat_sessions_manager.branches

    links = log_manager.get_chat_history_overview(current_user) if log_manager else []

    # Get rate limiting information if enabled
    requests_remaining: int | None = None if current_user is None else current_user.requests_remaining
    if rate_limit_interval:
        rate_limit_interval = rate_limit_interval * 1000 // 3
    rate_limiting_bool = bool(requests_remaining and rate_limit_interval and max_requests)
    rate_limiting_str: str = str(rate_limiting_bool).lower()

    user_management = True if current_user else False

    is_admin = current_user.admin if current_user else False
    
    return render_template(
        'chat_interface.html',
        conversation=None,
        buttons=chat_branches,                                  # dict
        links=links,                                            # List[dict]
        requests_remaining=requests_remaining,                  # None | int
        max_requests_remaining=max_requests,                    # None | int
        requests_remaining_interval_ms=rate_limit_interval,     # None | int
        rate_limiting=rate_limiting_str,                        # str
        user_management=user_management,                        # str
        main_logo_light=main_logo_light,                        # None | str
        main_logo_dark=main_logo_dark,                          # None | str
        chat_head=chat_head,                                    # None | str
        favicon=favicon,                                        # None | str
        app_name=app_name if app_name else "Maeser",            # str
        is_admin=is_admin,                                      # bool
    )
