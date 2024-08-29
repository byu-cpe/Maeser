"""
This module contains the controller for rendering the user management page.

© 2024 Carson Bush

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
