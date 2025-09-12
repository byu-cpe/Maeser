# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This module contains the controller for rendering the user management page.
"""

from flask import render_template
from maeser.user_manager import UserManager


def controller(
    user_manager: UserManager,
    app_name: str = "Maeser",
    main_logo_chat: str | None = None,
    favicon: str | None = None,
) -> str:
    """
    Render the user management page.

    Args:
        user_manager (UserManager): The user manager instance.
        app_name (str): The name of the application. Defaults to 'Maeser'.
        main_logo_chat (str | None): The dark version of the main logo.
            Defaults to None, in which case maeser/data/static/maeser-dark-header.png is used.
        favicon (str | None): The favicon image URL. Defaults to None, in which case
            maeser/data/static/maeser.png is used.

    Returns:
        str: The rendered HTML for the user management page.
    """
    return render_template(
        template_name_or_list="user_management.html",
        user_manager=user_manager,
        users=user_manager.list_users(),
        main_logo_chat=main_logo_chat,
        favicon=favicon,
        app_name=app_name,
        # Builtin functions not normally in Jinja templates
        len=len,
    )
