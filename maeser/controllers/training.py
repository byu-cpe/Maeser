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
        'train.html',
        role_options=role_options,
        type_options=type_options
    )