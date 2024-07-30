"""Module for handling feedback form display.

This module contains the controller function to render the feedback form template.

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

from flask import render_template

def controller(app_name: str | None = None, main_logo_light: str | None = None, main_logo_dark: str | None = None, favicon: str | None = None) -> str:
    """
    Display the feedback form.

    Returns:
        str: Rendered feedback form template.
    """
    role_options = ['Undergraduate Student', 'Graduate Student', 'Faculty', 'Other']
    category_options = ['Other', 'General Feedback', 'Bug Report', 'Feature Request', 'Content Issue']
    return render_template(
        'feedback_form.html', 
        role_options=role_options,
        category_options=category_options,
        main_logo_light=main_logo_light,
        main_logo_dark=main_logo_dark,
        favicon=favicon,
        app_name=app_name if app_name else "Maeser"
    )
