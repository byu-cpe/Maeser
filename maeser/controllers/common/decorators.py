# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This module contains decorators for rate limiting and admin access control
in a Flask application.
"""

from maeser.user_manager import UserManager, User
from functools import wraps
from flask import abort


def rate_limited(auth_manager: UserManager, current_user: User):
    """
    Decorator to rate limit an endpoint based on user's remaining requests.

    Aborts endpoint with code 429 if the user is out of requests.

    Args:
        auth_manager (UserManager): The authentication manager to handle request limits.
        current_user (User): The user object containing request information.

    Returns:
        A wrapped endpoint function that checks for rate limits.
    """

    def decorator(endpoint):
        @wraps(endpoint)
        def rate_limited_wrapper(*args, **kwargs):
            # Check if user has any requests remaining before proceeding
            if current_user.requests_remaining <= 0:
                print(f"User ({current_user.full_id_name}) has no requests remaining")
                abort(429, "Rate limit reached, please try again later")

            result = endpoint(*args, **kwargs)

            # Decrease the number of requests remaining for the user once response is sent and update the result
            auth_manager.decrease_requests(current_user.auth_method, current_user.ident)
            result["requests_remaining"] = auth_manager.get_requests_remaining(
                current_user.auth_method, current_user.ident
            )
            return result

        rate_limited_wrapper.__name__ = f"{endpoint.__name__}"

        return rate_limited_wrapper

    return decorator


def admin_required(current_user: User):
    """
    Decorator to ensure that an endpoint can only be accessed by an admin.

    Aborts endpoint with code 403 if user does not have admin access.

    Args:
        current_user (User): The user object to check for admin privileges.

    Returns:
        A wrapped endpoint function that checks for admin access.
    """

    def decorator(endpoint):
        @wraps(endpoint)
        def admin_wrapper(*args, **kwargs):
            if current_user.admin:
                print(f"User ({current_user.full_id_name}) is admin")
                return endpoint(*args, **kwargs)
            print(f"User ({current_user.full_id_name}) is not authorized")
            abort(403, "Admin access is required to access this page.")

        admin_wrapper.__name__ = f"{endpoint.__name__}"

        return admin_wrapper

    return decorator
