# SPDX-License-Identifier: LGPL-3.0-or-later

"""
User management API controller.

This module provides an API endpoint for managing users, including listing users,
toggling admin and banned statuses, updating request counts, removing users from
the cache, fetching users, listing cleanable users, and cleaning the cache.
"""

from typing import Any
from maeser.user_manager import UserManager
from flask import abort, request


def controller(
    user_manager: UserManager,
) -> list[dict[str, Any]] | dict[str, str] | list[Any]:
    """
    API endpoint for user management used by maeser/data/static/user-management.js.

    Uses flask.request and checks for a post request with the following fields:

    - "**type**" (*str*): The type of command to run.
    - "**user_auth**" (*str*): The ID of the user authenticator. Defaults to an empty string if the field is not provided.
    - "**user_id**" (*str*): The ID of the user. (**Note:** While the full ID of a user is ``authenticator.user_ident``, "**user_id**" is just ``user_ident``.) Defaults to an empty string if the field is not provided.

    The behavior of this controller depends on the command in "**type**":

    "**check-user-auth**":
        Checks if "**user_auth**" is a registered authentication method.

        **Returns:**
            ``{'is_auth_registered': True | False}``

    "**get-user**":
        Get's the User object (given "**user_auth**" and "**user_id**").

        **Returns:**
            json representation of User object.

    "**list-users**":
        Checks the post request for filter fields and returns a list of users that match those filters.
        The filter fields should include the following:

        - "**auth-filter**": The ID of one of the authenticators. Defaults to "All".
        - "**admin-filter**": "Admin", "Non-Admin", or "All" (default).
        - "**banned-filter**": "Banned", "Non-Banned", or "All" (default).

        **Returns:**
            list of User objects (in json format).

    "**toggle-admin**":
        Checks the post request for "**new_status**" and updates the user's admin status accordingly.
        "**new_status**" is a required field and should be either 'true' or 'false'.

        **Returns:**
            ``{'response': 'Made <auth_method>.<user_ident> an admin' | 'Made <auth_method>.<user_ident> no longer an admin'}``

    "**toggle-ban**":
        Checks the post request for "**new_status**" and updates the user's admin status accordingly.
        "**new_status**" is a required field and should be either 'true' or 'false'.

        **Returns:**
            ``{'response': 'Made <auth_method>.<user_ident> banned' | 'Made <auth_method>.<user_ident> no longer banned'}``

    "**update-requests**":
        Checks the post request for "**action**" and adds or removes a message request from the user according to the action.
        If "**action**" is "add", a request will be added; If "**action**" is "remove", a request will be removed.

        **Returns:**
            ``{'response': 'Updated <auth_method>.<user_ident> requests'}``

    "**remove-user**":
        Removes the user from the user database.
        If the post request provides "**force_remove**" and "**force_remove**" is set to 'true', then the controller will attempt
        to remove the user even if the user's authenticator is not currently registered. This may be helpful in removing users
        from authenticators that were once supported by the application but are no longer registered.

        **Returns:**
            ``{'response': 'Removed <auth_method>.<user_ident> from the cache'}``

    "**fetch-user**":
        Fetches a user from the authentication source and adds them to the cache without modifying their admin or banned status.

        **Returns:**
            ``{'response': 'Fetched <auth_method>.<user_ident>'}``

    "**list-cleanables**":
        Lists all non-banned and non-admin users in the cache/database.

        **Returns:**
            list of user identifiers in the format ``auth_method:user_id``.

    "**clean-cache**":
        Cleans the cache by removing all non-banned and non-admin users.

        **Returns:**
            ``{'response': 'Cleaned user cache'}``

    Args:
        user_manager (UserManager): User Manager object to interact with the user database.

    Returns:
        list[dict[str, Any]] | dict[str, str] | list[Any]: JSON response with the result of the command.

    **Aborts**:
        400: If the request is not JSON or a required parameter is missing.
    """
    if not request.is_json or request.json is None:
        return abort(400, "Request must be JSON")
    command = request.json.get("type")
    auth_method = request.json.get("user_auth", "")
    user_ident = request.json.get("user_id", "")

    if command == "check-user-auth":
        return {"is_auth_registered": user_manager.check_user_auth(auth_method)}

    if command == "get-user":
        if not (auth_method):
            return abort(400, "Missing user_auth")
        if not (user_ident):
            return abort(400, "Missing user_id")

        user = user_manager.get_user(auth_method, user_ident)
        return user.json

    if command == "list-users":
        # Get arguments for the filter by auth, admin, and banned status
        auth_filter = request.json.get("auth-filter", "all")
        admin_filter = request.json.get("admin-filter", "all")
        banned_filter = request.json.get("banned-filter", "all")
        user_list = [
            user.json
            for user in user_manager.list_users(
                auth_filter, admin_filter, banned_filter
            )
        ]
        return user_list

    elif command == "toggle-admin":
        new_status = request.json.get("new_status")
        if new_status is None:
            return abort(400, "Missing new_status")
        user_manager.update_admin_status(auth_method, user_ident, new_status)
        return {
            "response": f"Made {auth_method}.{user_ident} {'an admin' if new_status else 'no longer an admin'}"
        }

    elif command == "toggle-ban":
        new_status = request.json.get("new_status")
        if new_status is None:
            return abort(400, "Missing new_status")
        user_manager.update_banned_status(auth_method, user_ident, new_status)
        return {
            "response": f"Made {auth_method}.{user_ident} {'banned' if new_status else 'no longer banned'}"
        }

    elif command == "update-requests":
        sub_action = request.json.get("action")
        if sub_action is None:
            return abort(400, "Missing action")
        if sub_action == "add":
            user_manager.increase_requests(auth_method, user_ident)
        elif sub_action == "remove":
            user_manager.decrease_requests(auth_method, user_ident)
        else:
            return abort(400, f'Invalid action was given: "{sub_action}"')
        return {"response": f"Updated {auth_method}.{user_ident} requests"}

    elif command == "remove-user":
        force_remove = request.json.get("force_remove", False)
        user_manager.remove_user_from_cache(
            auth_method, user_ident, force_remove=force_remove
        )
        return {"response": f"Removed {auth_method}.{user_ident} from the cache"}

    elif command == "fetch-user":
        user_manager.fetch_user(auth_method, user_ident)
        return {"response": f"Fetched {auth_method}.{user_ident}"}

    elif command == "list-cleanables":
        return user_manager.list_cleanables()

    elif command == "clean-cache":
        user_manager.clean_cache()
        return {"response": "Cleaned user cache"}

    else:
        return abort(400, f'Invalid command type was given: "{command}"')
