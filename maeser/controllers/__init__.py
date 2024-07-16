from flask import Blueprint, abort
from jinja2 import TemplateNotFound

from . import (
    chat_interface,
    chat_logs_overview,
    chat_tests_overview,
    display_chat_log,
    display_chat_test,
    feedback_form,
    login,
    logout,
    new_session_handler,
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
    "new_session_handler",
    "training",
    "training_post",
    "chat_api",
    "conversation_history_api",
    "feedback_api",
    "remaining_requests_api",
    "common",
]

def build_flask_blueprint(log_path: str, chat_branches: list[dict], max_requests: int, rate_limit_interval: int, chat_session_manager, auth_manager, current_user) -> Blueprint:
    base_blueprint = Blueprint(
        "chat",
        __name__,
        template_folder="templates",
        static_folder="static",
        static_url_path="/static/maeser",
    )
    
    @base_blueprint.route("/chat")
    def chat_interface_endpoint():
        try:
            return chat_interface.controller(log_path, chat_branches, max_requests, rate_limit_interval)
        except TemplateNotFound:
            abort(404)
    
    @base_blueprint.route("/chat/<chat_id>", methods=["POST"])
    def chat_api_endpoint(chat_id):
        return chat_api.controller(chat_id, chat_session_manager)
    
    @base_blueprint.route("/conversation_history", methods=["POST"])
    def conversation_history_api_endpoint():
        return conversation_history_api.controller(chat_session_manager)
    
    @base_blueprint.route("/new_session", methods=["POST"])
    def new_session_handler_endpoint():
        return new_session_handler.controller(chat_session_manager)
    
    @base_blueprint.route("/get_requests_remaining", methods=["POST"])
    def remaining_requests_api_endpoint():
        return remaining_requests_api.controller(auth_manager, current_user)
    
    @base_blueprint.route("/response_feedback", methods=["POST"])
    def feedback_api_endpoint():
        return feedback_api.controller(chat_session_manager)
    
    @base_blueprint.route("/logs")
    def chat_logs_overview_endpoint():
        try:
            return chat_logs_overview.controller(log_path, chat_branches)
        except TemplateNotFound:
            abort(404)
    
    @base_blueprint.route("/tests")
    def chat_tests_overview_endpoint():
        try:
            return chat_tests_overview.controller(log_path + "/tests")
        except TemplateNotFound:
            abort(404)
    
    @base_blueprint.route("/logs/<branch>/<filename>")
    def display_chat_log_endpoint(branch, filename):
        try:
            return display_chat_log.controller(log_path, branch, filename)
        except TemplateNotFound:
            abort(404)
    
    @base_blueprint.route("/tests/<filename>/<int:conversation_index")
    def display_chat_test_endpoint(filename, conversation_index):
        try:
            return display_chat_test.controller(log_path, filename, conversation_index)
        except TemplateNotFound:
            abort(404)
    
    @base_blueprint.route("/feedback", methods=["POST"])
    def feedback_form_endpoint():
        return feedback_form.controller()

    @base_blueprint.route("/save_feedback", methods=["POST"])
    def save_feedback_form_endpoint():
        return save_feedback_form.controller(log_path)
    
    @base_blueprint.route("/training", methods=["GET"])
    def training_endpoint():
        return training.controller()
    
    @base_blueprint.route("/training", methods=["POST"])
    def training_post_endpoint():
        return training_post.controller(log_path)
    
    @base_blueprint.route("/login", methods=["GET", "POST"])
    def login_endpoint():
        return login.login_controller(auth_manager)
    
    @base_blueprint.route("/login/github")
    def github_login_endpoint():
        return login.github_authorize_controller(current_user, auth_manager.authenticators['github'])
    
    @base_blueprint.route("/login/github/callback")
    def github_callback_endpoint():
        return login.github_auth_callback_controller(current_user, auth_manager)
    
    @base_blueprint.route("/logout")
    def logout_endpoint():
        return logout.controller()
    
    return base_blueprint


