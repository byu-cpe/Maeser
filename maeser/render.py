# SPDX-License-Identifier: LGPL-3.0-or-later

"""
Markdown response conversion module. Intended for use with LLM output.

This module provides a utility function to easily customize HTML layouts and convert markdown
responses to HTML with additional processing, such as adding target="_blank" to anchor tags
and adjusting paths for images.
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
    html_content = markdown.markdown(
        text, extensions=["pymdownx.superfences", "tables", "smarty", "sane_lists"]
    )
    # Add target="_blank" attribute to anchor tags
    html_content = html_content.replace("<a href", '<a target="_blank" href')
    html_content = html_content.replace("figures/", "/figures/")
    return html_content
