"""
This module contains the controller function to display the training form.
"""

from flask import render_template

def controller(app_name: str | None = None, main_logo_login: str | None  = None, main_logo_chat: str | None = None, favicon: str | None = None) -> str:
    """
    Display the training form.

    Returns:
        str: Rendered training template.
    """
    role_options = ['Professor', 'Teachers Assistant']
    type_options = ['Information', 'Style']

    return render_template(
        'training.html',
        role_options=role_options,
        type_options=type_options,
        app_name=app_name if app_name else "Maeser",
        main_logo_login=main_logo_login,
        main_logo_chat=main_logo_chat,
        favicon=favicon
    )
