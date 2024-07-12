from flask import request
from flask_login import current_user

def sess_handler_controller(session_handler):
    """
    Handle session requests.

    Returns:
        dict: Response confirming session action.
    """
    posty = request.get_json()
    branch_action = posty["action"]
    if posty["type"] == "new":
        return {"response": session_handler.new_session(branch_action, current_user)}
    return {"response": "invalid", "details": "Requested session type is not valid"}