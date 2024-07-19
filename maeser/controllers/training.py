"""
This module contains the controller function to display the training form.

Functions:
    controller: Renders the training form template.
"""

from flask import render_template


def controller():
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
        type_options=type_options
    )
