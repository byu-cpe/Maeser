# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This module provides a controller for fetching the remaining requests for a user.
"""

from maeser.user_manager import UserManager, User


def controller(user_manager: UserManager, current_user: User) -> dict[str, int | None]:
    """Fetch the remaining requests for the current user.

    The response is formatted as ``{'requests_remaining': <remaining_requests>}``, where
    "remaining_requests" is the number of remaining requests for the user. This will
    have a value of None if **current_user** does not exist.

    Args:
        user_manager (UserManager): The user manager to use for fetching request data.
        current_user (User): The current user whose request data is being fetched.

    Returns:
        dict: A dictionary containing the number of requests remaining for the user.
    """
    return {
        "requests_remaining": user_manager.get_requests_remaining(
            current_user.auth_method, current_user.ident
        )
    }
