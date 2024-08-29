"""
This module provides a controller for fetching the remaining requests for a user.

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

def controller(auth_manager, current_user):
    """Fetch the remaining requests for the current user.

    Args:
        auth_manager: The authentication manager to use for fetching request data.
        current_user: The current user whose request data is being fetched.

    Returns:
        dict: A dictionary containing the number of requests remaining for the user.
    """
    return {'requests_remaining': auth_manager.get_requests_remaining(current_user.auth_method, current_user.ident)}
