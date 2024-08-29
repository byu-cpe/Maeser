"""Module for handling feedback for messages through a controller.

This module defines a controller function that processes feedback
for messages. The feedback includes information such as the branch,
session ID, message, whether it is a like or dislike, and the index
of the message.

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
