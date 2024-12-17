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

class app_manager:

    def __init__(self, 
        #app and app name
        app: Flask,
        app_name: str,
        #flask secret
        flask_secret_key: str,
        #managers
        chat_session_manager: ChatSessionManager, 
        user_manager: UserManager | None = None,
        #images
        main_logo_login: str | None = None,
        main_logo_chat: str | None = None,
        chat_head: str | None = None,
        favicon: str | None = None,
        #text
        login_text: str | None = None,
        changelog: str | None = None,
        chat_greeting: str = "Hello, how can I help you today?",
        branch_response: str = "Okay, I'll help you with ${action}!",
        #toggle animations
        animation: bool = False,
        #colors
        primary_color: str = "#333",
        secondary_color: str = "#ccc",
        button_color: str = "#0084ff",
        button_color_active: str = "#009e15", 
        button_color_inactive: str = "#e9e9e9", 
        fafa_button: str = "#b8b8b8",
        logout_button: str = "#000000",
        new_chat_button: str = "#000000",
        help_train_button: str = "#a8a8a8",
    ):
        """
        Initialize the HTML Manager

        Args:
            app (Flask): The Flask application instance.
            app_name (str | None, optional): The name of the application.
            flask_secret_key (str): The secret key for the Flask application.
            chat_session_manager (ChatSessionManager): The chat session manager instance.
            user_manager (UserManager | None, optional): The user manager instance. Defaults to None.
            main_logo_login (str | None, optional): URL or path to the login logo. Defaults to None.
            main_logo_chat (str | None, optional): URL or path to the chat logo. Defaults to None.
            chat_head (str | None, optional): URL or path to the chat header image. Defaults to None.
            favicon (str | None, optional): URL or path to the favicon. Defaults to None.
            login_text (str | None, optional): Text to display on the login page. Defaults to None.
            changelog (str | None, optional): Text to display as the changelog. Defaults to None.
            chat_greeting (str, optional): Greeting message to display in the chat. Defaults to "Hello, how can I help you today?".
            branch_response (str, optional): Response message to display when a branch is selected. Defaults to "Okay, I'll help you with ${action}!".
            animation (bool, optional): Whether to enable toggle animations. Defaults to False.
            primary_color (str, optional): Primary color of the application. Defaults to "#333".
            secondary_color (str, optional): Secondary color of the application. Defaults to "#ccc".
            button_color (str, optional): Color of the buttons. Defaults to "#0084ff".
            button_color_active (str, optional): Color of the active buttons. Defaults to "#009e15".
            button_color_inactive (str, optional): Color of the inactive buttons. Defaults to "#ddd".
            fafa_button (str, optional): Color of the fafa buttons. Defaults to "#eee".
            logout_button (str, optional): Color of the logout button. Defaults to "#333".
            new_chat_button (str, optional): Color of the new chat button. Defaults to "#333".
            help_train_button (str, optional): Color of the help train button. Defaults to "#eee".
        """
        self.app = app
        self.app_name = app_name

        self.flask_secret_key = flask_secret_key

        self.chat_session_manager = chat_session_manager
        self.user_manager = user_manager

        self.main_logo_login = main_logo_login
        self.main_logo_chat = main_logo_chat
        self.chat_head = chat_head
        self.favicon = favicon

        self.login_text = login_text
        self.changelog = changelog
        self.chat_greeting = chat_greeting
        self.branch_response = branch_response

        self.animation = animation

        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.button_color = button_color
        self.button_color_active = button_color_active
        self.button_color_inactive = button_color_inactive
        self.fafa_button = fafa_button
        self.logout_button = logout_button
        self.new_chat_button = new_chat_button
        self.help_train_button = help_train_button

        self.current_dir = os.path.dirname(os.path.abspath(__file__ + '/.'))

    def template_styles_css (self):
        """
        Template the styles.css file using Jinja2 templating
        """

    def template_chat_interface (self):
        """
        Template the chat_interface.html file using Jinja2 templating
        """

    def template_login (self):
        """
        Template the login.html file using Jinja2 templating
        """

    def template_training (self):
        """
        Template the training.html file using Jinja2 templating
        """

    def template_feedback (self):
        """
        Template the feedback_form.html file using Jinja2 templating
        """

    def add_flask_blueprint(
        self,
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
            template_folder=os.path.join(self.current_dir, 'data/templates'),
            static_folder=os.path.join(self.current_dir, 'data/static'),
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
