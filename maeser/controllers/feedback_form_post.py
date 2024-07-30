"""
Module for handling feedback form submissions.

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
from flask import request, redirect

def controller(chat_sessions_manager: ChatSessionManager):
    """
    Controller function to handle the feedback form submission.

    Args:
        chat_sessions_manager (ChatSessionManager): The manager for chat sessions.

    Returns:
        Response: Redirects to the home page.
    """

    chat_logs_manager = chat_sessions_manager.chat_logs_manager

    name = request.form.get('name')
    feedback = request.form.get('feedback')
    role = request.form.get('role')
    category = request.form.get('category')

    if chat_logs_manager is not None:
        chat_logs_manager.save_feedback({
            'name': name,
            'feedback': feedback,
            'role': role,
            'category': category
        })

    return redirect('/')
