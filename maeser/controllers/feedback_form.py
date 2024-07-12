from flask import render_template

def feedback_form_controller():
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
        category_options=category_options
    )