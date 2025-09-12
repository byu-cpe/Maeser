# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This module contains the controller function to display the training form.
"""

from flask import render_template


def controller(
    app_name: str = "Maeser",
    main_logo_chat: str | None = None,
    favicon: str | None = None,
) -> str:
    """Renders the training form template in HTML format.

    Args:
        app_name (str): The name of the application. Defaults to 'Maeser'.
        main_logo_chat (str | None): The dark version of the main logo.
            Defaults to None, in which case maeser/data/static/maeser-dark-header.png is used.
        favicon (str | None): The favicon image URL. Defaults to None, in which case
            maeser/data/static/maeser.png is used.

    Returns:
        str: The rendered training form page.
    """
    role_options = ["Professor", "Teachers Assistant"]
    type_options = ["Information", "Style"]

    return render_template(
        "training.html",
        role_options=role_options,
        type_options=type_options,
        app_name=app_name,
        main_logo_chat=main_logo_chat,
        favicon=favicon,
    )
