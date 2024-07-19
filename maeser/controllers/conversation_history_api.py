"""
Module for handling conversation history retrieval in a Flask API.

This module defines a controller function that retrieves the conversation history
for a given session and branch. The conversation history is processed to handle
system messages by applying HTML response formatting.
"""

from flask import jsonify, request

from .common.render import get_response_html


def controller(session_handler):
    """
    Retrieves the conversation history for a given session and branch.

    Args:
        session_handler (object): An object that handles session management
            and provides a method to retrieve conversation history.

    Returns:
        dict: A dictionary containing the conversation history, with system
            messages having their content processed by the `get_response_html` function.

    The function expects the request data to contain 'session' and 'branch' keys,
    which are used to retrieve the conversation history from the `session_handler` object.
    If the conversation history contains 'messages', it iterates through them and processes
    the content of system messages using the `get_response_html` function. Finally, it
    returns the conversation history as a JSON response.
    """
    data = request.get_json()

    session = data.get('session')
    branch = data.get('branch')
    
    conversation_history = session_handler.get_conversation_history(branch, session)
    if 'messages' in conversation_history:
        for message in conversation_history['messages']:
            if message['role'] == 'system':
                message['content'] = get_response_html(message['content'])
            else:
                message['content'] = message['content']

    return jsonify(conversation_history)
