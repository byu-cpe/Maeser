def controller(auth_manager, current_user):
    return {'requests_remaining': auth_manager.get_requests_remaining(current_user.auth_method, current_user.ident)}