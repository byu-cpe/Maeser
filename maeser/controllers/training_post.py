"""
This module contains functions to save training data and handle controller
requests in a Flask application.

Functions:
    save_training_data: Saves the training data to a log file.
    controller: Handles incoming POST requests for training data.
"""

from maeser.chat.chat_session_manager import ChatSessionManager
from flask import request, redirect
import time
from os import mkdir
import yaml


def save_training_data(log_path: str | None, training_data: dict) -> None:
    """
    Save the training data to a file in the log path.

    Args:
        log_path (str | None): The path where the training data logs are saved.
        training_data (dict): The training data to save.
    """
    try:
        mkdir(f'{log_path}/training_data')
    except FileExistsError:
        pass

    now = time.time()
    timestamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(now))
    filename = f'{log_path}/training_data/{timestamp}.log'

    with open(filename, 'w') as f:
        yaml.dump(training_data, f)

    print(f'Training data saved to {filename}')


def controller(chat_session_manager: ChatSessionManager):
    """
    Handle the POST request to save training data.

    Args:
        chat_session_manager (ChatSessionManager): The chat session manager instance.
    """
    name = request.form.get('name')
    role = request.form.get('role')
    type = request.form.get('type')
    question = request.form.get('question')
    answer: str | None = request.form.get('answer')

    save_training_data(chat_session_manager.chat_log_path, {
        'name': name,
        'role': role,
        'type': type,
        'question': question,
        'answer': answer
    })

    return redirect('/')
