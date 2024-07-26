"""
This module contains functions to save training data and handle controller
requests in a Flask application.

Functions:
    save_training_data: Saves the training data to a log file.
    controller: Handles incoming POST requests for training data.
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
