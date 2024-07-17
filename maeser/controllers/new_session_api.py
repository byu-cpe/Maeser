from maeser.chat.chat_session_manager import ChatSessionManager
from flask import request
from flask_login import current_user

def controller(session_handler: ChatSessionManager, user_management: bool = False):
    """
    Handle session requests.

    Returns:
        dict: Response confirming session action.
    """
    posty = request.get_json()
    branch_action = posty["action"]
    if posty["type"] == "new":
        return {"response": session_handler.get_new_session_id(branch_action, current_user)} if user_management else {"response": session_handler.get_new_session_id(branch_action)}
    return {"response": "invalid", "details": "Requested session type is not valid"}