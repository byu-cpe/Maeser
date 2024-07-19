"""Logout controller for handling user logouts and session cleanup."""

from flask_login import logout_user
from flask import redirect, url_for, session

def controller():
    """Handles user logout and session cleanup.

    Logs out the user and removes specific session keys related to the user identity.
    
    Args:
        None

    Returns:
        flask.Response: A redirect response to the login page.
    """
    logout_user()
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    return redirect(url_for('maeser.login'))