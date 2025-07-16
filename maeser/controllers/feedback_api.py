"""Module for handling feedback for messages through a controller.

This module defines a controller function that processes feedback
for messages. The feedback includes information such as the branch,
session ID, message, whether it is a like or dislike, and the index
of the message.
"""

from maeser.chat.chat_session_manager import ChatSessionManager
from flask import request

def controller(session_handler: ChatSessionManager):
    """
    Handle feedback for messages.

    Args:
        session_handler (ChatSessionManager): The session handler to
            manage chat sessions and feedback.

    Returns:
        dict: Status of the feedback submission.
    """
    data = request.get_json()
    branch = data.get('branch')
    session_id = data.get('session_id')
    message = data.get('message')
    like = data.get('like')
    index = int(data.get('index'))
    print(f'Received feedback: {"Like" if like else "Dislike"} for message: {message} at index: {index}')
    # Handle the feedback (e.g., save to a database, log it, etc.)
    session_handler.add_feedback(branch, session_id, index, like)
    return {'status': 'success'}
