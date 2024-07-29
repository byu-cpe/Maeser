from maeser.user_manager import UserManager
from flask import abort, request

def controller(user_manager: UserManager):
    """
    API endpoint for user management.

    Args:
        user_manager (UserManager): User Manager object to interact with the user database.

    """
    if not request.is_json or request.json is None:
        return abort(400, 'Request must be JSON')
    command = request.json.get('type')
    print(f'{type(command)}: {command}')
    print(request.json)
    if command == 'list-users':
        # get arguments for the filter by auth, admin, and banned status
        auth_filter = request.json.get('auth-filter', 'all')
        admin_filter = request.json.get('admin-filter', 'all')
        banned_filter = request.json.get('banned-filter', 'all')
        user_list = [user.json for user in user_manager.list_users(auth_filter, admin_filter, banned_filter)]
        return user_list
    else:
        return abort(400, f'Invalid command type was given: "{command}"')