import yaml
from flask import abort, render_template

from .common.render import get_response_html

from typing import Dict, Any

def get_test_file_template(content: Dict[str, Any], conversation_index: int, filename: str) -> str:
    """
    Get the test file template.

    Args:
        content (dict): The content of the test file.
        conversation_index (int): The index of the conversation to display.
        filename (str): The name of the test file.
    
    Returns:
        str: The test file template.
    """


    version = content.get("version", "unknown")
    test_num = content.get("test-num", "unknown")
    conversations = content.get("conversations", "unknown")

    if not isinstance(conversations, list) or conversation_index >= len(conversations):
        raise ValueError(f"Invalid conversation index: {conversation_index}")

    conversation: Dict[str, Any] = conversations[conversation_index]

    metrics = conversation.get("metrics", {})
    context = conversation.get("contexts", {})

    question = get_response_html(conversation.get("question", ""))
    answer = get_response_html(conversation.get("answer", ""))
    branch = conversation.get("branch", "")

    return render_template(
        'test_file.html',
        version=version,
        test_num=test_num,
        question=question,
        answer=answer,
        branch=branch,
        metrics=metrics,
        context=context,
        conversation_index=conversation_index,
        num_conversations=len(conversations),
        filename=filename
    )

def controller(test_yaml_path: str, filename: str, conversation_index: str):
    """
    Display the content of a specified test file.

    Args:
        filename (str): The name of the test file.
        conversation_index (int): The index of the conversation.
    
    Returns:
        str: Rendered template with test file content.
    """
    try:
        with open(f"{test_yaml_path}/{filename}", "r") as file:
            file_content = yaml.safe_load(file)
        test_template = get_test_file_template(file_content, int(conversation_index), filename)
        return test_template
    except FileNotFoundError:
        abort(404, description="Test file not found")
    except yaml.YAMLError as e:
        abort(500, description=f"Error parsing test file: {e}")
    except ValueError as e:
        abort(400, description=str(e))
