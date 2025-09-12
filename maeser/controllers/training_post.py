# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This module contains the controller to save training data from a post request.
"""

from maeser.chat.chat_session_manager import ChatSessionManager
from flask import request, redirect, Response


def controller(chat_session_manager: ChatSessionManager) -> Response:
    """
    Handle the post request to save training data.

    Uses flask.request and expects a post request with the following fields:

    - "**name**": The name of the form respondent.
    - "**role**": The role/position of the respondent. Expected values are "Professor" or "Teachers Assistant".
    - "**type**": The type of training data. Expected values are "Information" or "Style".
    - "**question**": The question the user would ask the chatbot.
    - "**answer**": The answer the chatbot should generate in response to the user's question.

    Args:
        chat_session_manager (ChatSessionManager): The chat session manager instance.

    Returns:
        Response: Redirects to the home page.
    """
    chat_logs_manager = chat_session_manager.chat_logs_manager

    name = request.form.get("name")
    role = request.form.get("role")
    type = request.form.get("type")
    question = request.form.get("question")
    answer: str | None = request.form.get("answer")

    if chat_logs_manager is not None:
        chat_logs_manager.save_training_data(
            {
                "name": name,
                "role": role,
                "type": type,
                "question": question,
                "answer": answer,
            }
        )

    return redirect("/")
