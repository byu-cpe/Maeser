from os import mkdir
import time
import yaml
from flask import request, redirect, url_for

def save_feedback(log_path: str, feedback: dict) -> None:
    """
    Save the feedback to a file in the log path.

    Args:
        feedback (dict): The feedback to save.
    """

    # make directory if it doesn't exist
    try:
        mkdir(f"{log_path}/feedback")
    except FileExistsError:
        pass

    now = time.time()
    timestamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(now))
    filename = f"{log_path}/feedback/{timestamp}.log"

    with open(filename, "w") as f:
        yaml.dump(feedback, f)

    print(f"Feedback saved to {filename}")

def controller():
    name = request.form.get('name')
    feedback = request.form.get('feedback')
    role = request.form.get('role')
    category = request.form.get('category')

    save_feedback({
        'name': name,
        'feedback': feedback,
        'role': role,
        'category': category
    })
    
    return redirect(url_for('main_page'))