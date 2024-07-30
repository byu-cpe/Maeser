"""
This module contains functions for processing and rendering chat logs.

It includes functions to process messages, get the log file template, and display
the content of a specified log file.

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
