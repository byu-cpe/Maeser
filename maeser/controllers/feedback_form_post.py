"""
Module for handling feedback form submissions.
"""

from maeser.chat.chat_session_manager import ChatSessionManager
from os import mkdir
import time
import yaml
from flask import request, redirect

def save_feedback(log_path: str | None, feedback: dict) -> None:
    """
    Save the feedback to a file in the log path.

    Args:
        log_path (str | None): The path where the feedback should be saved.
        feedback (dict): The feedback to save.
    """

    # Make directory if it doesn't exist
    try:
        mkdir(f'{log_path}/feedback')
    except FileExistsError:
        pass

    now = time.time()
    timestamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(now))
    filename = f'{log_path}/feedback/{timestamp}.log'

    with open(filename, 'w') as f:
        yaml.dump(feedback, f)

    print(f'Feedback saved to {filename}')

def controller(chat_sessions_manager: ChatSessionManager):
    """
    Controller function to handle the feedback form submission.

    Args:
        chat_sessions_manager (ChatSessionManager): The manager for chat sessions.

    Returns:
        Response: Redirects to the home page.
    """

    name = request.form.get('name')
    feedback = request.form.get('feedback')
    role = request.form.get('role')
    category = request.form.get('category')

    save_feedback(chat_sessions_manager.chat_log_path, {
        'name': name,
        'feedback': feedback,
        'role': role,
        'category': category
    })

    return redirect('/')
