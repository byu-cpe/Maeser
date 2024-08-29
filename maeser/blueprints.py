"""
Blueprint definitions for the Maeser application.

This module sets up the Flask blueprint and associated routes for the Maeser
application. It includes route handlers for chat interfaces, user management,
feedback, and training functionalities.

© 2024 Blaine Freestone, Carson Bush

This file is part of Maeser.

Maeser is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

Maeser is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with
Maeser. If not, see <https://www.gnu.org/licenses/>.
"""

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
    """
    Add the Maeser blueprint to the Flask application.

    Args:
        app (Flask): The Flask application instance.
        flask_secret_key (str): The secret key for the Flask application.
        chat_session_manager (ChatSessionManager): The chat session manager instance.
        user_manager (UserManager | None, optional): The user manager instance. Defaults to None.
        app_name (str | None, optional): The name of the application. Defaults to None.
        main_logo_light (str | None, optional): URL or path to the light logo. Defaults to None.
        main_logo_dark (str | None, optional): URL or path to the dark logo. Defaults to None.
        chat_head (str | None, optional): URL or path to the chat header image. Defaults to None.
        favicon (str | None, optional): URL or path to the favicon. Defaults to None.

    Returns:
        Flask: The Flask application instance with the blueprint registered.
    """
    maeser_blueprint = Blueprint(
        'maeser',
        __name__,
        template_folder=os.path.join(current_dir, 'data/templates'),
        static_folder=os.path.join(current_dir, 'data/static'),
        static_url_path='/maeser/static',
    )

    @maeser_blueprint.app_template_filter('datetimeformat')
    def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
        """Format a timestamp as a datetime string."""
        return datetime.fromtimestamp(value).strftime(format)

    if user_manager:
        def refresh_requests():
            """Refresh user requests at regular intervals."""
            while True:
                time.sleep(user_manager.rate_limit_interval)
                user_manager.refresh_requests()

        threading.Thread(target=refresh_requests, daemon=True).start()

        app.secret_key = flask_secret_key
        login_manager = LoginManager(app)
        login_manager.init_app(app)
        login_manager.login_view = 'maeser.login'  # type: ignore
        login_manager.session_protection = 'strong'
        
        @login_manager.user_loader
        def load_user(user_full_id: str):
            """Load a user by their ID."""
            auth_method, user_id = user_full_id.split('.', 1)
            return user_manager.get_user(auth_method, user_id)

        @maeser_blueprint.route('/')
        @login_required
        def chat_interface_route():
            """Route for the chat interface."""
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
            """Route for the login interface."""
            return login_api.login_controller(
                user_manager,
                main_logo_light=main_logo_light,
                main_logo_dark=main_logo_dark,
                favicon=favicon,
                app_name=app_name
            )
        
        @maeser_blueprint.route('/login/github', methods=['GET'])
        def github_authorize():
            """Route for GitHub authorization."""
            return login_api.github_authorize_controller(
                current_user, 
                user_manager.authenticators['github']
            )

        @maeser_blueprint.route('/login/github_callback')
        def github_auth_callback():
            """Route for GitHub authorization callback."""
            return login_api.github_auth_callback_controller(
                current_user, 
                user_manager,
                main_logo_light=main_logo_light,
                main_logo_dark=main_logo_dark,
                favicon=favicon,
                app_name=app_name
            )

        @maeser_blueprint.route('/logout')
        @login_required
        def logout_route():
            """Route for logging out."""
            return logout.controller()
        
        @maeser_blueprint.route('/users')
        @login_required
        @admin_required(current_user)
        def manage_users():
            """Route for managing users."""
            return manage_users_view.controller(
                user_manager, 
                main_logo_light=main_logo_light, 
                main_logo_dark=main_logo_dark, 
                favicon=favicon, 
                app_name=app_name
            )
        
        @maeser_blueprint.route('/users/api', methods=['POST'])
        @login_required
        @admin_required(current_user)
        def manage_users_api():
            """API route for managing users."""
            return user_management_api.controller(user_manager)

        @maeser_blueprint.route('/req_session', methods=['POST'])
        @login_required
        def sess_handler():
            """Route for handling session requests."""
            return new_session_api.controller(chat_session_manager, True)
        
        @maeser_blueprint.route('/msg/<chat_session>', methods=['POST'])
        @login_required
        @rate_limited(user_manager, current_user)
        def msg_api(chat_session):
            """API route for handling chat messages."""
            return chat_api.controller(chat_session_manager, chat_session)
        
        @maeser_blueprint.route('/feedback', methods=['POST'])
        @login_required
        def feedback():
            """Route for submitting feedback."""
            return feedback_api.controller(chat_session_manager)
        
        @app.route('/get_requests_remaining', methods=['GET'])
        @login_required
        def get_requests_remaining():
            """Route for getting the remaining requests."""
            return remaining_requests_api.controller(user_manager, current_user)

    else:
        @maeser_blueprint.route('/')
        def chat_interface_route():
            """Route for the chat interface."""
            return chat_interface.controller(
                chat_session_manager,
                main_logo_light=main_logo_light,
                main_logo_dark=main_logo_dark,
                favicon=favicon,
                chat_head=chat_head,
                app_name=app_name
            )

        @maeser_blueprint.route('/req_session', methods=['POST'])
        def sess_handler():
            """Route for handling session requests."""
            return new_session_api.controller(chat_session_manager)
        
        @maeser_blueprint.route('/msg/<chat_session>', methods=['POST'])
        def msg_api(chat_session):
            """API route for handling chat messages."""
            return chat_api.controller(chat_session_manager, chat_session)
        
        @maeser_blueprint.route('/feedback', methods=['POST'])
        def feedback():
            """Route for submitting feedback."""
            return feedback_api.controller(chat_session_manager)

    if chat_session_manager.chat_logs_manager:
        @maeser_blueprint.route('/train')
        @login_required if user_manager else lambda x: x
        def train():
            """Route for training."""
            return training.controller(
                main_logo_dark=main_logo_dark,
                main_logo_light=main_logo_light,
                favicon=favicon,
                app_name=app_name,
            )

        @maeser_blueprint.route('/submit_train', methods=['POST'])
        @login_required if user_manager else lambda x: x
        def submit_train():
            """Route for submitting training data."""
            return training_post.controller(chat_session_manager)

        @maeser_blueprint.route('/feedback_form')
        def feedback_form():
            """Route for getting the feedback form."""
            return feedback_form_get.controller(
                main_logo_dark=main_logo_dark,
                main_logo_light=main_logo_light,
                favicon=favicon,
                app_name=app_name,
            )

        @maeser_blueprint.route('/submit_feedback', methods=['POST'])
        def submit_feedback():
            """Route for submitting feedback."""
            return feedback_form_post.controller(chat_session_manager)
        
        @maeser_blueprint.route('/logs', methods=['GET'])
        @login_required if user_manager else lambda x: x
        @admin_required(current_user) if user_manager else lambda x: x
        def logs():
            """Route for viewing chat logs."""
            return chat_logs_overview.controller(
                chat_session_manager,
                favicon=favicon,
                app_name=app_name
            )

        @maeser_blueprint.route('/logs/<branch>/<filename>')
        @login_required if user_manager else lambda x: x
        @admin_required(current_user) if user_manager else lambda x: x
        def display_log(branch, filename):
            """Route for displaying a specific chat log."""
            return display_chat_log.controller(
                chat_session_manager, branch, filename, app_name=app_name
            )

        @maeser_blueprint.route('/conversation_history', methods=['POST'])
        @login_required if user_manager else lambda x: x
        def conversation_history():
            """Route for getting conversation history."""
            return conversation_history_api.controller(chat_session_manager)

    app.register_blueprint(maeser_blueprint)
    return app
