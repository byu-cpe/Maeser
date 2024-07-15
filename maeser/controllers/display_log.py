import yaml
from flask import abort, render_template

from .common.render import get_response_html


def process_messages(messages: dict) -> dict:
    """
    Process each system response in the conversation and convert it to HTML.

    Args:
        messages (dict): The messages in the conversation.
    
    Returns:
        dict: The processed messages in HTML format.
    """
    for message in messages:
        message["content"] = get_response_html(message["content"])
    
    return messages

def get_log_file_template(content: dict) -> str:
    """
    Get the log file template.

    Args:
        content (dict): The content of the log file.
    
    Returns:
        str: The log file template.
    """
    user_name = content['user']
    real_name = content['real_name']
    branch = content["branch"]
    time = content["time"]
    total_cost = round(content["total_cost"], 3)
    total_tokens = content["total_tokens"]
    
    try:
        messages = process_messages(content["messages"])
    except KeyError:
        messages = None
    
    return render_template(
        'log_file.html',
        user_name=user_name,
        real_name=real_name,
        branch=branch,
        time=time,
        total_cost=total_cost,
        total_tokens=total_tokens,
        messages=messages
    )

def controller(chat_log_path: str, branch, filename):
    """
    Display the content of a specified log file.

    Args:
        branch (str): The branch where the log file is located.
        filename (str): The name of the log file.
    
    Returns:
        str: Rendered template with log file content.
    """
    try:
        with open(f"{chat_log_path}/chat_history/{branch}/{filename}", "r") as file:
            file_content = yaml.safe_load(file)
        log_template = get_log_file_template(file_content)
        return log_template
    except FileNotFoundError:
        abort(404, description="Log file not found")
    except yaml.YAMLError as e:
        abort(500, description=f"Error parsing log file: {e}")