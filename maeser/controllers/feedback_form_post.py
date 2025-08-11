# SPDX-License-Identifier: LGPL-3.0-or-later

"""
Module for handling feedback form submissions.
"""

from maeser.chat.chat_session_manager import ChatSessionManager
from flask import request, redirect, Response


def controller(chat_sessions_manager: ChatSessionManager) -> Response:
    """
    Controller function to handle the feedback form submission.

    Uses flask.request and expects a post request with the following fields:

    - "**name**": The name of the form respondent.
    - "**feedback**": The text content of the feedback submitted by the respondent.
    - "**role**": The role/position of the respondent. Expected values are "Undergraduate Student", "Graduate Student", "Faculty", or "Other".
    - "**category**": The category of the feedback. Expected values are "General Feedback", "Bug Report", "Feature Request", "Content Issue", or "Other".

    Args:
        chat_sessions_manager (ChatSessionManager): The manager for chat sessions.

    Returns:
        Response: Redirects to the home page.
    """

    chat_logs_manager = chat_sessions_manager.chat_logs_manager

    name = request.form.get("name")
    feedback = request.form.get("feedback")
    role = request.form.get("role")
    category = request.form.get("category")

    if chat_logs_manager is not None:
        chat_logs_manager.save_feedback(
            {"name": name, "feedback": feedback, "role": role, "category": category}
        )

    return redirect("/")
