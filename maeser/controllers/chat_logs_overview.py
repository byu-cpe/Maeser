"""
This module contains the controller function for rendering the chat logs overview page.

It handles fetching log files, applying filters, and calculating aggregate data such as total tokens and cost.
"""

from maeser.chat.chat_session_manager import ChatSessionManager

import yaml
from .common.file_info import get_file_list
from flask import render_template, request


def controller(chat_sessions_manager: ChatSessionManager, favicon: str | None = None) -> str:
    """
    Render the home page with log files and aggregate token and cost data.

    Args:
        chat_sessions_manager (ChatSessionManager): An instance of ChatSessionManager to manage chat sessions.

    Returns:
        str: Rendered home template with log file list.
    """
    log_path = chat_sessions_manager.chat_log_path
    chat_branches = chat_sessions_manager.branches

    sort_by = request.args.get('sort_by', 'modified')  # Default sorting by modification time
    order = request.args.get('order', 'desc')  # Default sorting order is descending
    branch_filter = request.args.get('branch', '')
    feedback_filter = request.args.get('feedback', None)

    print(chat_branches)
    log_files = get_file_list(log_path + '/chat_history') if log_path else []
    branches = [branch for branch in chat_branches] if chat_branches else []

    if branch_filter:
        log_files = [f for f in log_files if branch_filter.lower() in f['branch'].lower()]

    if feedback_filter:
        feedback_filter = feedback_filter.lower() == 'true'
        log_files = [f for f in log_files if f['has_feedback'] == feedback_filter]

    reverse = (order == 'desc')
    log_files.sort(key=lambda x: x[sort_by], reverse=reverse)

    # Calculate aggregate number of tokens and cost
    total_tokens = 0
    total_cost = 0.0
    for file in log_files:
        with open(f"{log_path}/chat_history/{file['branch']}/{file['name']}", 'r') as log_file:
            file_content = yaml.safe_load(log_file)
            total_tokens += file_content.get('total_tokens', 0)
            total_cost += file_content.get('total_cost', 0.0)

    return render_template('chat_logs_overview.html', 
                            log_files=log_files, 
                            branches=branches, 
                            sort_by=sort_by, 
                            order=order, 
                            branch_filter=branch_filter, 
                            feedback_filter=feedback_filter,
                            total_tokens=total_tokens, 
                            total_cost=total_cost,
                            favicon=favicon
                            )