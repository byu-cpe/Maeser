"""
This module contains the controller for rendering the user management page.
"""

from flask import render_template
from maeser.user_manager import UserManager

def controller(
    user_manager: UserManager,
    app_name: str | None = None,
    main_logo_light: str | None = None,
    main_logo_dark: str | None = None,
    chat_head: str | None = None,
    favicon: str | None = None,
):
    """
    Render the user management page.

    Args:
        user_manager (UserManager): The user manager instance.
        app_name (str | None, optional): The name of the application. Defaults to None.
        main_logo_light (str | None, optional): The light version of the main logo. Defaults to None.
        main_logo_dark (str | None, optional): The dark version of the main logo. Defaults to None.
        chat_head (str | None, optional): The chat head image URL. Defaults to None.
        favicon (str | None, optional): The favicon image URL. Defaults to None.

    Returns:
        str: The rendered HTML for the user management page.
    """
    return render_template(
        template_name_or_list='user_management.html',
        user_manager=user_manager,
        users=user_manager.list_users(),
        main_logo_light=main_logo_light,
        main_logo_dark=main_logo_dark,
        chat_head=chat_head,
        favicon=favicon,
        app_name=app_name if app_name else 'Maeser',
        # Builtin functions not normally in Jinja templates
        len=len,
    )
