# SPDX-License-Identifier: LGPL-3.0-or-later

"""
Module for handling conversation history retrieval in a Flask API.

This module defines a controller function that retrieves the conversation history
for a given session and branch. The conversation history is processed to handle
system messages by applying HTML response formatting.
"""

from flask import jsonify, request
from maeser.chat.chat_session_manager import ChatSessionManager
from maeser.render import get_response_html


def controller(session_handler: ChatSessionManager) -> dict:
    """
    Retrieves the conversation history for a given session and branch.

    The function uses flask.request and expects a post request that contains 'session' and 'branch' keys,
    which are used to retrieve the conversation history from **session_handler**.
    If the conversation history contains 'messages', it iterates through them and processes
    the content of system messages using **maeser.render.get_response_html()**. Finally, it
    returns the conversation history as a JSON response.

    Args:
        session_handler (ChatSessionManager): The chat session manager for the Maeser application.

    Returns:
        dict: A dictionary containing the conversation history, with system
            messages having their content processed by **get_response_html()**.
    """
    data = request.get_json()

    session = data.get("session")
    branch = data.get("branch")

    conversation_history = session_handler.get_conversation_history(branch, session)
    if "messages" in conversation_history:
        for message in conversation_history["messages"]:
            if message["role"] == "system":
                message["content"] = get_response_html(message["content"])
            else:
                message["content"] = message["content"]

    return jsonify(conversation_history)
