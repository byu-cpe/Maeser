# SPDX-License-Identifier: LGPL-3.0-or-later

"""
Module for handling login and GitHub OAuth2 authorization controllers.
"""

from maeser.user_manager import UserManager, User, GithubAuthenticator
from flask import render_template, redirect, url_for, request, session, Response
from typing import Union
from flask_login import login_user, current_user
from urllib.parse import urljoin, urlparse


def is_safe_url(target: str) -> bool:
    """Checks if a URL is safe for redirection.

    Args:
        target (str): The target URL to check.

    Returns:
        bool: True if the URL is safe, False otherwise.
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def login_controller(
    auth_manager: UserManager,
    app_name: str | None = None,
    main_logo_login: str | None = None,
    main_logo_chat: str | None = None,
    favicon: str | None = None,
) -> Union[Response, str]:
    """Handles user login.

    Args:
        auth_manager (UserManager): The authentication manager to handle user authentication.
        app_name (str | None): The display name of the Maeser application.
            This will be populated into the page's title element. Defaults to None.
        main_logo_login (str | None): The main logo to display on the login page.
            Defaults to None, in which case it will use maeser/data/static/maeser.png.
        main_logo_chat (str | None): Currently unused. This logo would populate into the page header,
            but the login page currently does not have a page header. This may change in the future.
        favicon (str | None): The favicon for the page. Defaults to None, in which case it will
            use maeser/data/static/maeser.png.

    Returns:
        Response | str: A redirect to home if the user is authenticated, or the rendered login page if the user is not authenticated.
    """
    if current_user is not None and current_user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        auth_method = request.form.get("authvalidator", "invalid")
        if auth_method == "invalid":
            return render_template(
                "login.html",
                message="Invalid Authentication Method in Request",
                main_logo_login=main_logo_login,
                main_logo_chat=main_logo_chat,
                favicon=favicon,
                app_name=app_name if app_name else "Maeser",
                authenticators=auth_manager.authenticators,
            )
        user = auth_manager.authenticate(auth_method, username, password)
        if user is None:
            return render_template(
                "login.html",
                message="Authentication Failed",
                main_logo_login=main_logo_login,
                main_logo_chat=main_logo_chat,
                favicon=favicon,
                app_name=app_name if app_name else "Maeser",
                authenticators=auth_manager.authenticators,
            )
        if not user.is_active:
            return render_template(
                "login.html",
                message=f"User {user.full_id_name} is Banned",
                main_logo_login=main_logo_login,
                main_logo_chat=main_logo_chat,
                favicon=favicon,
                app_name=app_name if app_name else "Maeser",
                authenticators=auth_manager.authenticators,
            )

        login_user(user)

        next_url = request.args.get("next")
        if not next_url or not is_safe_url(next_url):
            next_url = "/"

        return redirect(next_url)

    next_url = request.args.get("next")
    message = request.args.get("message", "")

    return render_template(
        "login.html",
        message=message,
        next=next_url,
        main_logo_login=main_logo_login,
        main_logo_chat=main_logo_chat,
        favicon=favicon,
        app_name=app_name if app_name else "Maeser",
        authenticators=auth_manager.authenticators,
    )


def github_authorize_controller(
    current_user: User, github_authenticator: GithubAuthenticator
) -> Response:
    """Handles GitHub OAuth2 authorization.

    Updates '**oauth2_state**' in the Flask session and redirects the user to the
    GitHub authorization url.

    Args:
        current_user (User): The currently logged-in user.
        github_authenticator (GitHubAuthenticator): The GitHub authenticator to get OAuth2 info.

    Returns:
        Response: The response object to redirect to the OAuth2 provider.
    """
    if not current_user.is_anonymous:
        return redirect("/")

    session["oauth2_state"], provider_url = github_authenticator.get_auth_info()
    session.modified = True
    print(f"OAuth2 state: {session['oauth2_state']}")

    # Redirect the user to the OAuth2 provider authorization URL
    return redirect(provider_url)


def github_auth_callback_controller(
    current_user: User, auth_manager: UserManager, login_redirect: str = "maeser.login"
) -> Response:
    """Redirects the user after authentication is complete. Handles cases where authentication is unsuccessful.

    Redirects the user back to the login page if authentication fails or the home page if authentication is successful.

    Args:
        current_user (User): The user being authenticated.
        auth_manager (UserManager): The user manager for the Maeser application.
        login_redirect (str, optional): The URL to redirect to if authentication fails. Defaults to 'maeser.login'.

    Returns:
        Response: The corresponding URL to redirect to.
    """

    if not current_user.is_anonymous:
        return redirect("/")

    # If there was an error before auth, render the login page with the error message
    if "error" in request.args:
        print(
            f"An error occurred during the auth callback before authentication: {request.args}"
        )
        error_message = request.args.get("error_description", "Authentication failed")
        return redirect(url_for(login_redirect, message=error_message))

    oauth_state = session.get("oauth2_state")
    print(f"OAuth2 state at callback: {oauth_state}")

    user = auth_manager.authenticate("github", request.args, oauth_state)
    if user is None:
        return redirect(url_for(login_redirect, message="GitHub Authentication Failed"))
    if not user.is_active:
        return redirect(
            url_for(login_redirect, message=f"User {user.full_id_name} is Banned")
        )

    login_user(user)

    return redirect("/")
