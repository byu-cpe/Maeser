# SPDX-License-Identifier: LGPL-3.0-or-later

"""Module for handling feedback form display.

This module contains the controller function to render the feedback form template.
"""

from flask import render_template

def controller(app_name: str | None = None, main_logo_chat: str | None = None, favicon: str | None = None) -> str:
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
        main_logo_chat=main_logo_chat,
        favicon=favicon,
        app_name=app_name if app_name else "Maeser"
    )
