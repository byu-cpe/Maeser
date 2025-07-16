"""
Module for handling feedback form submissions.
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
