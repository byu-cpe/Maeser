from email import message
from flask import Blueprint, session
from flask_login import login_required, LoginManager, current_user
import os
from datetime import datetime

import maeser
from maeser.chat.chat_session_manager import ChatSessionManager
from maeser.controllers.common.decorators import rate_limited, admin_required
from maeser.user_manager import UserManager
from . import (
    chat_api,
    chat_interface,
    chat_logs_overview,
    chat_tests_overview,
    display_chat_log,
    display_chat_test,
    feedback_api,
    feedback_form_get,
    feedback_form_post,
    login_api,
    logout,
    new_session_api,
    training,
    training_post,
)
from . import chat_api, conversation_history_api, feedback_api, remaining_requests_api
from . import common

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__ + '/..'))

def get_maeser_blueprint_with_user_management(chat_session_manager: ChatSessionManager, user_manager: UserManager) -> Blueprint:
    maeser_blueprint = Blueprint(
        "maeser",
        __name__,
        template_folder=os.path.join(current_dir, 'data/templates'),
        static_folder=os.path.join(current_dir, 'data/static'),
        static_url_path="/maeser/static",
    )

    @maeser_blueprint.app_template_filter('datetimeformat')
    def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
        return datetime.fromtimestamp(value).strftime(format)
    
    @maeser_blueprint.route("/")
    @login_required
    def chat_interface_route():
        return chat_interface.controller(
            chat_session_manager
        )

    @maeser_blueprint.route('/login', methods=['GET', 'POST'])
    def login():
        return login_api.login_controller(user_manager)
    
    @maeser_blueprint.route('/login/github', methods=["GET"])
    def github_authorize():
        return login_api.github_authorize_controller(current_user, user_manager)

    @maeser_blueprint.route('/login/github_callback')
    def github_auth_callback():
        print('goofy, ah, callback')
        return login_api.github_auth_callback_controller(current_user, user_manager)

    return maeser_blueprint

def get_maeser_blueprint_without_user_management(chat_session_manager: ChatSessionManager) -> Blueprint:
    maeser_blueprint = Blueprint(
        "maeser",
        __name__,
        template_folder=os.path.join(current_dir, 'data/templates'),
        static_folder=os.path.join(current_dir, 'data/static'),
        static_url_path="/maeser/static",
    )

    @maeser_blueprint.app_template_filter('datetimeformat')
    def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
        return datetime.fromtimestamp(value).strftime(format)

    @maeser_blueprint.route("/")
    def chat_interface_route():
        return chat_interface.controller(
            chat_session_manager
        )
    
    @maeser_blueprint.route("/req_session", methods=["POST"])
    def sess_handler():
        return new_session_api.controller(chat_session_manager)
    
    @maeser_blueprint.route("/msg/<chat_session>", methods=["POST"])
    def msg_api(chat_session):
        return chat_api.controller(chat_session_manager, chat_session)
    
    @maeser_blueprint.route('/feedback', methods=['POST'])
    def feedback():
        return feedback_api.controller(chat_session_manager)

    if chat_session_manager.chat_logs_manager:
        @maeser_blueprint.route("/train")
        def train():
            return training.controller()

        @maeser_blueprint.route("/submit_train", methods=["POST"])
        def submit_train():
            return training_post.controller(chat_session_manager)

        @maeser_blueprint.route("/feedback_form")
        def feedback_form():
            return feedback_form_get.controller()

        @maeser_blueprint.route("/submit_feedback", methods=["POST"])
        def submit_feedback():
            return feedback_form_post.controller(chat_session_manager)
        
        @maeser_blueprint.route('/logs', methods=['GET'])
        def logs():
            return chat_logs_overview.controller(chat_session_manager)

        @maeser_blueprint.route("/logs/<branch>/<filename>")
        def display_log(branch, filename):
            return display_chat_log.controller(chat_session_manager, branch, filename)

        @maeser_blueprint.route("/conversation_history", methods=["POST"])
        def conversation_history():
            return conversation_history_api.controller(chat_session_manager)

    return maeser_blueprint