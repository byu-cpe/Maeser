from flask import Blueprint, Flask
from flask_login import login_required, current_user, LoginManager
import os
from datetime import datetime
import threading
import time

from maeser.chat.chat_session_manager import ChatSessionManager
from maeser.controllers.common.decorators import admin_required, rate_limited
from maeser.user_manager import UserManager
from .controllers import (
    chat_api,
    chat_interface,
    chat_logs_overview,
    display_chat_log,
    feedback_api,
    feedback_form_get,
    feedback_form_post,
    login_api,
    logout,
    new_session_api,
    training,
    training_post,
    conversation_history_api,
    remaining_requests_api,
    manage_users_view,
    user_management_api,
)

current_dir = os.path.dirname(os.path.abspath(__file__ + '/.'))

def add_flask_blueprint(
        app: Flask,
        flask_secret_key: str,
        chat_session_manager: ChatSessionManager, 
        user_manager: UserManager | None = None,
        app_name: str | None = None,
        main_logo_light: str | None = None,
        main_logo_dark: str | None = None,
        chat_head: str | None = None,
        favicon: str | None = None,
    ) -> Flask:

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

    if user_manager:
        def refresh_requests():
            while True:
                time.sleep(user_manager.rate_limit_interval)
                user_manager.refresh_requests()

        threading.Thread(target=refresh_requests, daemon=True).start()

        app.secret_key = flask_secret_key  # Replace with a secure secret key
        login_manager = LoginManager(app)
        login_manager.init_app(app)
        login_manager.login_view = "maeser.login"   # type: ignore
        login_manager.session_protection = "strong"
        
        @login_manager.user_loader
        def load_user(user_full_id: str):
            auth_method, user_id = user_full_id.split('.', 1)
            return user_manager.get_user(auth_method, user_id)

        @maeser_blueprint.route("/")
        @login_required
        def chat_interface_route():
            return chat_interface.controller(
                chat_session_manager, 
                user_manager.max_requests, 
                user_manager.rate_limit_interval, 
                current_user, 
                main_logo_light=main_logo_light,
                main_logo_dark=main_logo_dark,
                favicon=favicon,
                chat_head=chat_head,
                app_name=app_name
            )

        @maeser_blueprint.route('/login', methods=['GET', 'POST'])
        def login():
            return login_api.login_controller(
                user_manager,
                main_logo_light=main_logo_light,
                main_logo_dark=main_logo_dark,
                favicon=favicon,
                app_name=app_name
            )
        
        @maeser_blueprint.route('/login/github', methods=["GET"])
        def github_authorize():
            return login_api.github_authorize_controller(
                current_user, 
                user_manager.authenticators['github']
            )

        @maeser_blueprint.route('/login/github_callback')
        def github_auth_callback():
            return login_api.github_auth_callback_controller(
                current_user, 
                user_manager,
                main_logo_light=main_logo_light,
                main_logo_dark=main_logo_dark,
                favicon=favicon,
                app_name=app_name
            )

        @maeser_blueprint.route("/logout")
        @login_required
        def logout_route():
            return logout.controller()
        
        @maeser_blueprint.route("/users")
        @login_required
        @admin_required(current_user)
        def manage_users():
            return manage_users_view.controller(user_manager, main_logo_light=main_logo_light, main_logo_dark=main_logo_dark, favicon=favicon, app_name=app_name)
        
        @maeser_blueprint.route("/users/api", methods=["POST"])
        @login_required
        @admin_required(current_user)
        def manage_users_api():
            return user_management_api.controller(user_manager)

        @maeser_blueprint.route("/req_session", methods=["POST"])
        @login_required
        def sess_handler():
            return new_session_api.controller(chat_session_manager, True)
        
        @maeser_blueprint.route("/msg/<chat_session>", methods=["POST"])
        @login_required
        @rate_limited(user_manager, current_user)
        def msg_api(chat_session):
            return chat_api.controller(chat_session_manager, chat_session)
        
        @maeser_blueprint.route('/feedback', methods=['POST'])
        @login_required
        def feedback():
            return feedback_api.controller(chat_session_manager)
        
        @app.route("/get_requests_remaining", methods=["GET"])
        @login_required
        def get_requests_remaining():
            return remaining_requests_api.controller(user_manager, current_user)

    else:
        @maeser_blueprint.route("/")
        def chat_interface_route():
            return chat_interface.controller(
                chat_session_manager,
                main_logo_light=main_logo_light,
                main_logo_dark=main_logo_dark,
                favicon=favicon,
                chat_head=chat_head,
                app_name=app_name
            )

        @maeser_blueprint.route("/req_session", methods=["POST"])
        def sess_handler():
            return new_session_api.controller(
                chat_session_manager
            )
        
        @maeser_blueprint.route("/msg/<chat_session>", methods=["POST"])
        def msg_api(chat_session):
            return chat_api.controller(
                chat_session_manager, 
                chat_session
            )
        
        @maeser_blueprint.route('/feedback', methods=['POST'])
        def feedback():
            return feedback_api.controller(
                chat_session_manager
            )

    if chat_session_manager.chat_logs_manager:
        @maeser_blueprint.route("/train")
        @login_required if user_manager else lambda x: x
        def train():
            return training.controller(
                main_logo_dark=main_logo_dark,
                main_logo_light=main_logo_light,
                favicon=favicon,
                app_name=app_name,
            )

        @maeser_blueprint.route("/submit_train", methods=["POST"])
        @login_required if user_manager else lambda x: x
        def submit_train():
            return training_post.controller(
                chat_session_manager
            )

        @maeser_blueprint.route("/feedback_form")
        def feedback_form():
            return feedback_form_get.controller(
                main_logo_dark=main_logo_dark,
                main_logo_light=main_logo_light,
                favicon=favicon,
                app_name=app_name,
            )

        @maeser_blueprint.route("/submit_feedback", methods=["POST"])
        def submit_feedback():
            return feedback_form_post.controller(chat_session_manager)
        
        @maeser_blueprint.route('/logs', methods=['GET'])
        @login_required if user_manager else lambda x: x
        @admin_required(current_user) if user_manager else lambda x: x
        def logs():
            return chat_logs_overview.controller(
                chat_session_manager,
                favicon=favicon,
                app_name=app_name
            )

        @maeser_blueprint.route("/logs/<branch>/<filename>")
        @login_required if user_manager else lambda x: x
        @admin_required(current_user) if user_manager else lambda x: x
        def display_log(branch, filename):
            return display_chat_log.controller(chat_session_manager, branch, filename, app_name=app_name)

        @maeser_blueprint.route("/conversation_history", methods=["POST"])
        @login_required if user_manager else lambda x: x
        def conversation_history():
            return conversation_history_api.controller(chat_session_manager)

    app.register_blueprint(maeser_blueprint)
    return app