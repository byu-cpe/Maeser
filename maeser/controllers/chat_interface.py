from typing import List

from flask import render_template
from flask_login import current_user

from .common.file_info import get_file_list


def controller(log_path: str, chat_branches: List[dict], max_requests: int, rate_limit_interval: int):
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
        'chat.html', 
        conversation=None, 
        buttons=chat_branches, 
        links=links,
        requests_remaining=requests_remaining,
        max_requests_remaining=max_requests,
        requests_remaining_interval_ms=rate_limit_interval * 1000 / 3
    )
