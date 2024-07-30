"""
This module contains functions to save training data and handle controller
requests in a Flask application.

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

def controller(chat_session_manager: ChatSessionManager):
    """
    Handle the POST request to save training data.

    Args:
        chat_session_manager (ChatSessionManager): The chat session manager instance.
    """
    chat_logs_manager = chat_session_manager.chat_logs_manager
    
    name = request.form.get('name')
    role = request.form.get('role')
    type = request.form.get('type')
    question = request.form.get('question')
    answer: str | None = request.form.get('answer')

    if chat_logs_manager is not None:
        chat_logs_manager.save_training_data({
            'name': name,
            'role': role,
            'type': type,
            'question': question,
            'answer': answer
        })

    return redirect('/')
