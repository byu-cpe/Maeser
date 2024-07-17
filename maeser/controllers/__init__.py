from email import message
from flask import Blueprint, session
import os

import maeser
from maeser.chat.chat_session_manager import ChatSessionManager
from . import (
    chat_api,
    chat_interface,
    chat_logs_overview,
    chat_tests_overview,
    display_chat_log,
    display_chat_test,
    feedback_api,
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

def get_maeser_blueprint_without_user_management(chat_session_manager: ChatSessionManager) -> Blueprint:
    maeser_blueprint_without_user_management = Blueprint(
        "maeser",
        __name__,
        template_folder=os.path.join(current_dir, 'data/templates'),
        static_folder=os.path.join(current_dir, 'data/static'),
        static_url_path="/maeser/static",
    )

    @maeser_blueprint_without_user_management.route("/")
    def chat_interface_route():
        return chat_interface.controller(
            chat_session_manager
        )
    
    @maeser_blueprint_without_user_management.route("/req_session", methods=["POST"])
    def sess_handler():
        return new_session_api.controller(chat_session_manager)
    
    @maeser_blueprint_without_user_management.route("/msg/<chat_session>", methods=["POST"])
    def msg_api(chat_session):
        return chat_api.controller(chat_session_manager, chat_session)
    
    @maeser_blueprint_without_user_management.route('/feedback', methods=['POST'])
    def feedback():
        return feedback_api.controller(chat_session_manager)

    return maeser_blueprint_without_user_management