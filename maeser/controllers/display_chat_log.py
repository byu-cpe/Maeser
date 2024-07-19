"""
This module contains functions for processing and rendering chat logs.

It includes functions to process messages, get the log file template, and display
the content of a specified log file.
"""

from maeser.chat.chat_session_manager import ChatSessionManager
import yaml
from flask import abort, render_template

from .common.render import get_response_html


def process_messages(messages: dict) -> dict:
    """
    Process each system response in the conversation and convert it to HTML.

    Args:
        messages (dict): The messages in the conversation.
    
    Returns:
        dict: The processed messages in HTML format.
    """
    for message in messages:
        message['content'] = get_response_html(message['content'])
    
    return messages

def get_log_file_template(content: dict, app_name: str | None = None) -> str:
    """
    Get the log file template.

    Args:
        content (dict): The content of the log file.
    
    Returns:
        str: The log file template.
    """
    user_name = content['user']
    real_name = content['real_name']
    branch = content['branch']
    time = content['time']
    total_cost = round(content['total_cost'], 3)
    total_tokens = content['total_tokens']
    
    try:
        messages = process_messages(content['messages'])
    except KeyError:
        messages = None
    
    return render_template(
        'display_chat_log.html',
        user_name=user_name,
        real_name=real_name,
        branch=branch,
        time=time,
        total_cost=total_cost,
        total_tokens=total_tokens,
        messages=messages,
        app_name=app_name if app_name else "Maeser"
    )

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
    chat_log_path = chat_sessions_manager.chat_log_path
    
    try:
        with open(f'{chat_log_path}/chat_history/{branch}/{filename}', 'r') as file:
            file_content = yaml.safe_load(file)
        log_template = get_log_file_template(file_content, app_name)
        return log_template
    except FileNotFoundError:
        abort(404, description='Log file not found')
    except yaml.YAMLError as e:
        abort(500, description=f'Error parsing log file: {e}')
