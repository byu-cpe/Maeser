"""
This module contains functions for processing and rendering chat logs.

It includes functions to process messages, get the log file template, and display
the content of a specified log file.
"""

from maeser.chat.chat_session_manager import ChatSessionManager
from flask import abort

def controller(chat_sessions_manager: ChatSessionManager, branch, filename, app_name: str | None = None):
    """
    Display the content of a specified log file.

    Args:
        chat_sessions_manager (ChatSessionManager): The chat sessions manager instance.
        branch (str): The branch where the log file is located.
        filename (str): The name of the log file.
    
    Returns:
        str: Rendered template with log file content.
    
    Raises:
        FileNotFoundError: If the log file is not found.
        yaml.YAMLError: If there is an error parsing the log file.
    """
    chat_logs_manager = chat_sessions_manager.chat_logs_manager
    
    return chat_logs_manager.get_log_file_template(filename, branch) if chat_logs_manager else abort(404)
