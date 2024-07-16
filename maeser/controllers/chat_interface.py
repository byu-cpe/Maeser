from typing import List

from flask import render_template
from flask_login import current_user

from .common.file_info import get_file_list


def controller(log_path: str, chat_branches: List[dict], max_requests: int, rate_limit_interval: int):
    """
    Renders the chat interface template with relevant data.

    Args:
        log_path (str): The path to the directory containing chat history logs.
        chat_branches (List[dict]): A list of dictionaries representing available chat branches.
        max_requests (int): The maximum number of requests a user can make.
        rate_limit_interval (int): The interval in seconds for rate limiting requests.

    Returns:
        The rendered chat.html template with the following data:
            - conversation: None (no active conversation)
            - buttons: The list of available chat branches
            - links: A list of dictionaries representing previous chat sessions for the current user
            - requests_remaining: The number of requests remaining for the current user
            - max_requests_remaining: The maximum number of requests allowed
            - requests_remaining_interval_ms: The interval in milliseconds for rate limiting requests
    """
    links = []
    conversations = get_file_list(log_path + '/chat_history')
    for conversation in conversations:
        if current_user.full_id_name == conversation['user']:
            links.append({
                "branch": conversation['branch'],
                "session": conversation['name'].removesuffix('.log'),
                "modified": conversation['modified'],
                "first_message": conversation['first_message']
            })
    # sort conversations by date modified
    links.sort(key=lambda x: x['modified'], reverse=True)
    # remove conversations with no messages
    links = [link for link in links if link['first_message'] is not None]
    requests_remaining = current_user.requests_remaining

    return render_template(
        'chat_interface.html', 
        conversation=None, 
        buttons=chat_branches, 
        links=links,
        requests_remaining=requests_remaining,
        max_requests_remaining=max_requests,
        requests_remaining_interval_ms=rate_limit_interval * 1000 / 3
    )
