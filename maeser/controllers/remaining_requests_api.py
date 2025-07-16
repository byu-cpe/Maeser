"""
This module provides a controller for fetching the remaining requests for a user.
"""

def controller(auth_manager, current_user):
    """Fetch the remaining requests for the current user.

    Args:
        auth_manager: The authentication manager to use for fetching request data.
        current_user: The current user whose request data is being fetched.

    Returns:
        dict: A dictionary containing the number of requests remaining for the user.
    """
    return {'requests_remaining': auth_manager.get_requests_remaining(current_user.auth_method, current_user.ident)}
