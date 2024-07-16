from flask import Blueprint
import os

from . import (
    chat_interface,
    chat_logs_overview,
    chat_tests_overview,
    display_chat_log,
    display_chat_test,
    feedback_form,
    login,
    logout,
    new_session_api,
    save_feedback_form,
    training,
    training_post,
)
from . import chat_api, conversation_history_api, feedback_api, remaining_requests_api
from . import common

__all__ = [
    "chat_interface",
    "chat_logs_overview",
    "chat_tests_overview",
    "display_chat_log",
    "display_chat_test",
    "feedback_form",
    "save_feedback_form",
    "login",
    "logout",
    "new_session_api",
    "training",
    "training_post",
    "chat_api",
    "conversation_history_api",
    "feedback_api",
    "remaining_requests_api",
    "common",
]

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__ + '/..'))

# Use this blueprint routing controllers if you wish to use the built-in templates
maeser_blueprint = Blueprint(
    "maeser",
    __name__,
    template_folder=os.path.join(current_dir, 'data/templates'),
    static_folder=os.path.join(current_dir, 'data/static'),
    static_url_path="/static/maeser",
)
