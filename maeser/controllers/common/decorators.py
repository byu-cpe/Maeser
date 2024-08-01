"""
This module contains decorators for rate limiting and admin access control
in a Flask application.

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

from functools import wraps
from flask import abort

def rate_limited(auth_manager, current_user):
    """
    Decorator to rate limit an endpoint based on user's remaining requests.

    Args:
        auth_manager: The authentication manager to handle request limits.
        current_user: The user object containing request information.

    Returns:
        A wrapped endpoint function that checks for rate limits.
    """
    def decorator(endpoint):
        @wraps(endpoint)
        def rate_limited_wrapper(*args, **kwargs):
            # Check if user has any requests remaining before proceeding
            if current_user.requests_remaining <= 0:
                print(f'User ({current_user.full_id_name}) has no requests remaining')
                abort(429, 'Rate limit reached, please try again later')

            result = endpoint(*args, **kwargs)

            # Decrease the number of requests remaining for the user once response is sent and update the result
            auth_manager.decrease_requests(current_user.auth_method, current_user.ident)
            result['requests_remaining'] = auth_manager.get_requests_remaining(current_user.auth_method, current_user.ident)
            return result
        
        rate_limited_wrapper.__name__ = f'{endpoint.__name__}'

        return rate_limited_wrapper
    return decorator

def admin_required(current_user):
    """
    Decorator to ensure that an endpoint can only be accessed by an admin.

    Args:
        current_user: The user object to check for admin privileges.

    Returns:
        A wrapped endpoint function that checks for admin access.
    """
    def decorator(endpoint):
        @wraps(endpoint)
        def admin_wrapper(*args, **kwargs):
            if current_user.admin:
                print(f'User ({current_user.full_id_name}) is admin')
                return endpoint(*args, **kwargs)
            print(f'User ({current_user.full_id_name}) is not authorized')
            abort(403, 'Admin access is required to access this page.')
        
        admin_wrapper.__name__ = f'{endpoint.__name__}'
        
        return admin_wrapper
    return decorator
