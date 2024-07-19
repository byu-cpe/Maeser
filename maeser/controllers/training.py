from flask import render_template

def controller(app_name: str | None = None, main_logo_light: str | None  = None, main_logo_dark: str | None = None, favicon: str | None = None) -> str:
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
        main_logo_light=main_logo_light,
        main_logo_dark=main_logo_dark,
        favicon=favicon
    )