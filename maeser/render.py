"""
Markdown response conversion module. Intended for use with LLM output.

This module provides a utility function to convert markdown responses to HTML
with additional processing, such as adding target="_blank" to anchor tags and
adjusting paths for images.

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
