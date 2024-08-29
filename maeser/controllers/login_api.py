"""
Module for handling login and GitHub OAuth2 authorization controllers.

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

from flask import render_template, redirect, url_for, request, session
from flask_login import login_user, current_user
from urllib.parse import urljoin, urlparse

def controller():
    """Raises NotImplementedError for unimplemented controllers.

    This function should be replaced with a specific login controller 
    implementation, such as 'login_controller', 'github_authorize_controller', 
    or 'github_auth_callback_controller'.
    """
    raise NotImplementedError('Please import specify the login controller you want ("login_controller", "github_authorize_controller", "github_auth_callback_controller")')

def is_safe_url(target):
    """Checks if a URL is safe for redirection.

    Args:
        target (str): The target URL to check.

    Returns:
        bool: True if the URL is safe, False otherwise.
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def login_controller(auth_manager, app_name: str | None = None, main_logo_light: str | None = None, main_logo_dark: str | None = None, favicon: str | None = None):
    """Handles user login.

    Args:
        auth_manager (AuthManager): The authentication manager to handle user authentication.

    Returns:
        Response: The response object to render the login page or redirect.
    """
    if current_user is not None and current_user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        auth_method = request.form.get('authvalidator', 'invalid')
        if auth_method == 'invalid':
            return render_template(
                'login.html',
                message='Invalid Authentication Method in Request',
                main_logo_light=main_logo_light,
                main_logo_dark=main_logo_dark,
                favicon=favicon,
                app_name=app_name if app_name else "Maeser",
                authenticators=auth_manager.authenticators,
            )
        user = auth_manager.authenticate(auth_method, username, password)
        if user is None:
            return render_template(
                'login.html', 
                message='Authentication Failed',
                main_logo_light=main_logo_light,
                main_logo_dark=main_logo_dark,
                favicon=favicon,
                app_name=app_name if app_name else "Maeser",
                authenticators=auth_manager.authenticators,
            )
        if not user.is_active:
            return render_template(
                'login.html', 
                message=f'User {user.full_id_name} is Banned',
                main_logo_light=main_logo_light,
                main_logo_dark=main_logo_dark,
                favicon=favicon,
                app_name=app_name if app_name else "Maeser",
                authenticators=auth_manager.authenticators,
            )

        login_user(user)

        next_url = request.args.get('next')
        if not next_url or not is_safe_url(next_url):
            next_url = '/'

        return redirect(next_url)

    next_url = request.args.get('next')
    message = request.args.get('message', '')

    return render_template(
        'login.html', 
        message=message, 
        next=next_url,
        main_logo_light=main_logo_light,
        main_logo_dark=main_logo_dark,
        favicon=favicon,
        app_name=app_name if app_name else "Maeser",
        authenticators=auth_manager.authenticators,
    )

def github_authorize_controller(current_user, github_authenticator):
    """Handles GitHub OAuth2 authorization.

    Args:
        current_user (User): The currently logged-in user.
        github_authenticator (GitHubAuthenticator): The GitHub authenticator to get OAuth2 info.

    Returns:
        Response: The response object to redirect to the OAuth2 provider.
    """
    if not current_user.is_anonymous:
        return redirect('/')

    session['oauth2_state'], provider_url = github_authenticator.get_auth_info()
    session.modified = True
    print(f'OAuth2 state: {session["oauth2_state"]}')

    # Redirect the user to the OAuth2 provider authorization URL
    return redirect(provider_url)

def github_auth_callback_controller(current_user, auth_manager, app_name: str | None = None, main_logo_light: str | None = None, main_logo_dark: str | None = None, favicon: str | None = None, login_redirect: str = 'maeser.login'):
    if not current_user.is_anonymous:
        return redirect('/')

    # If there was an error before auth, render the login page with the error message
    if 'error' in request.args:
        print(f'An error occurred during the auth callback before authentication: {request.args}')
        error_message = request.args.get('error_description', 'Authentication failed')
        return redirect(url_for(login_redirect, message=error_message))
    
    oauth_state = session.get('oauth2_state')
    print(f'OAuth2 state at callback: {oauth_state}')

    user = auth_manager.authenticate('github', request.args, oauth_state)
    if user is None:
        return redirect(url_for(login_redirect, message='GitHub Authentication Failed'))
    if not user.is_active:
        return redirect(url_for(login_redirect, message=f'User {user.full_id_name} is Banned'))
    
    login_user(user)

    return redirect('/')
