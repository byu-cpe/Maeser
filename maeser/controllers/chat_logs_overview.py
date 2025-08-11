# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This module contains the controller function for rendering the chat logs overview page.

It handles fetching log files, applying filters, and calculating aggregate data such as total tokens and cost.
"""

from maeser.chat.chat_session_manager import ChatSessionManager

from flask import render_template, request


def controller(
    chat_sessions_manager: ChatSessionManager,
    app_name: str = "Maeser",
    main_logo_chat: str | None = None,
    favicon: str | None = None,
) -> str:
    """
    Renders the home page with log files and aggregate token and cost data.

    Args:
        chat_sessions_manager (ChatSessionManager): An instance of ChatSessionManager to manage chat sessions.
        app_name (str): The name of the app. This will be populated in the page's title element and header. Defaults to 'Maeser'.
        main_logo_chat (str | None): The dark version of the main logo.
            Defaults to None, in which case maeser/data/static/maeser-dark-header.png is used.
        favicon (str | None): The favicon image URL. Defaults to None, in which case
            maeser/data/static/maeser.png is used.

    Returns:
        str: Rendered home template with log file list.
    """
    chat_logs_manager = chat_sessions_manager.chat_logs_manager
    chat_branches = chat_sessions_manager.branches

    sort_by: str = request.args.get(
        "sort_by", "modified"
    )  # Default sorting by modification time
    order = request.args.get("order", "desc")  # Default sorting order is descending
    branch_filter = request.args.get("branch", "")
    user_filter = request.args.get("user", "")
    feedback_filter = request.args.get("feedback", None)

    chat_logs_overview, total_tokens, total_cost, users = (
        chat_logs_manager.get_chat_logs_overview(
            sort_by, order, branch_filter, user_filter, feedback_filter
        )
        if chat_logs_manager
        else []
    )
    branches = [branch for branch in chat_branches] if chat_branches else []

    return render_template(
        "chat_logs_overview.html",
        log_files=chat_logs_overview,
        branches=branches,
        sort_by=sort_by,
        order=order,
        branch_filter=branch_filter,
        user_filter=user_filter,
        feedback_filter=feedback_filter,
        total_tokens=total_tokens,
        total_cost=total_cost,
        users=users,
        main_logo_chat=main_logo_chat,
        favicon=favicon,
        app_name=app_name,
    )
