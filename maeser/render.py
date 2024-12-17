"""
Markdown response conversion module. Intended for use with LLM output.

This module provides a utility function to easily customize HTML layouts and convert markdown 
responses to HTML with additional processing, such as adding target="_blank" to anchor tags 
and adjusting paths for images.

© 2024 Carson Bush, Blaine Freestone

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

import markdown

def get_response_html(response: str) -> str:
    """
    Convert a markdown response to HTML.

    Args:
        response (str): The markdown response.

    Returns:
        str: The HTML response.
    """
    text = response
    html_content = markdown.markdown(text, extensions=['pymdownx.superfences', 'tables', 'smarty', 'sane_lists'])
    # Add target="_blank" attribute to anchor tags
    html_content = html_content.replace('<a href', '<a target="_blank" href')
    html_content = html_content.replace('figures/', '/figures/')
    return html_content

class html_manager:

    def __init__(self, 
        #app name
        app_name: str = "Maeser",
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
        button_color_inactive: str = "#ddd", 
        fafa_button: str = "#eee",
        logout_button: str = "#333",
        new_chat_button: str = "#333",
        help_train_button: str = "#eee",
    ):
        """
        Initialize the HTML Manager

        Args:
            app_name (str | None, optional): The name of the application. Defaults to Maeser.
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