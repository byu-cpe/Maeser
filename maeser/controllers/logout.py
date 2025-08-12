# SPDX-License-Identifier: LGPL-3.0-or-later

"""
Logout controller for handling user logouts and session cleanup.
"""

from flask_login import logout_user
from flask import redirect, url_for, session, Response


def controller() -> Response:
    """Handles user logout and session cleanup.

    Logs out the user and removes specific session keys related to the user identity.

    Returns:
        Response: A redirect response to the login page.
    """
    logout_user()
    for key in ("identity.name", "identity.auth_type"):
        session.pop(key, None)
    return redirect(url_for("maeser.login"))
