from flask import request, redirect
import time
from os import mkdir
import yaml

def save_training_data(log_path: str, training_data: dict) -> None:
    """
    Save the training data to a file in the log path.

    Args:
        training_data (dict): The training data to save.
    """

    # make directory if it doesn't exist
    try:
        mkdir(f"{log_path}/training_data")
    except FileExistsError:
        pass

    now = time.time()
    timestamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(now))
    filename = f"{log_path}/training_data/{timestamp}.log"

    with open(filename, "w") as f:
        yaml.dump(training_data, f)

    print(f"Training data saved to {filename}")

def controller(log_path: str):
    name = request.form.get('name')
    role = request.form.get('role')
    type = request.form.get('type')
    question = request.form.get('question')
    answer = request.form.get('answer')

    save_training_data(log_path,{
        'name': name,
        'role': role,
        'type': type,
        'question': question,
        'answer': answer
    
    })

    return redirect('/')