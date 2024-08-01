"""
This module contains the controller function for rendering the chat logs overview page.

It handles fetching log files, applying filters, and calculating aggregate data such as total tokens and cost.

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

from flask import render_template, request


def controller(chat_sessions_manager: ChatSessionManager, app_name: str | None = None, favicon: str | None = None) -> str:
    """
    Render the home page with log files and aggregate token and cost data.

    Args:
        chat_sessions_manager (ChatSessionManager): An instance of ChatSessionManager to manage chat sessions.

    Returns:
        str: Rendered home template with log file list.
    """
    chat_logs_manager = chat_sessions_manager.chat_logs_manager
    chat_branches = chat_sessions_manager.branches

    sort_by: str = request.args.get('sort_by', 'modified')  # Default sorting by modification time
    order = request.args.get('order', 'desc')  # Default sorting order is descending
    branch_filter = request.args.get('branch', '')
    feedback_filter = request.args.get('feedback', None)

    chat_logs_overview, total_tokens, total_cost = chat_logs_manager.get_chat_logs_overview(sort_by, order, branch_filter, feedback_filter) if chat_logs_manager else []
    branches = [branch for branch in chat_branches] if chat_branches else []

    return render_template(
        'chat_logs_overview.html', 
        log_files=chat_logs_overview, 
        branches=branches, 
        sort_by=sort_by, 
        order=order, 
        branch_filter=branch_filter, 
        feedback_filter=feedback_filter,
        total_tokens=total_tokens, 
        total_cost=total_cost,
        favicon=favicon,
        app_name=app_name if app_name else "Maeser",
    )