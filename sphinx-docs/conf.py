# SPDX-License-Identifier: LGPL-3.0-or-later

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../maeser'))
sys.path.insert(0, os.path.abspath('../tests'))

# Add all maeser dependencies that autodoc should pretend to import here.
# If autodoc fails because "module 'foo' has no attribute 'bar'", try adding it below.
autodoc_mock_imports = [
    'langchain',
    'langchain_core',
    'langchain_community',
    'langchain_openai',
    'langchain-text-splitters',
    'python-frontmatter',
    'faiss-cpu',
    'markdown',
    'langchain_text_splitters',
    'openai',
    'PyYAML',
    'frontmatter',
    'ragas',
    'seaborn',
    'datasets',
    'langgraph',
    'tiktoken',
    'PIL',
    'pydantic',
    'markdownify',
    # 'werkzeug',
    'flask',
    'flask-login',
    'flask_login',
    'pytest',
    'ldap3',
    # maeser[discord] dependencies
    'discord',
    # maeser[admin_portal] dependencies
    "pymupdf",
    "pymupdf4llm",
]

# -- Project information -----------------------------------------------------

project = 'Maeser'
author = 'The Maeser Team [PLACEHOLDER: Replaced with content in _static/js/dynamic-footer-disclaimers.js].'
copyright = '2025 [PLACEHOLDER: Replaced with content in _static/js/dynamic-footer-disclaimers.js]'

# The full version, including alpha/beta/rc tags
release = 'alpha'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_copybutton',
    'sphinxcontrib.mermaid',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '.sphinx-venv']

# -- Options for sphinx-copybutton -------------------------------------------
# Strip input prompts
# These use regular expressions to match the prompts that should be stripped from the code blocks.
# If you are having issues with copying, you can try changing these to better match your terminal prompts.
copybutton_custom_prompts = [
    r'^[^$#\n]*\$ ',        # bash
    r'>>> |\.\.\. ',        # Python Repl + continuation
    r'^(?:\S)*> ',          # Windows CMD/Powershell
]
copybutton_prompt_text = r'|'.join(copybutton_custom_prompts)
copybutton_prompt_is_regexp = True
copybutton_line_continuation_character = '\\'

# Ignore code blocks with the no-copybutton class. Ex:
# ```{code-block}
# :class: no-copybutton
# <code>
# ```
copybutton_selector = "div:not(.no-copybutton) > div.highlight > pre"

# -- Options for MyST --------------------------------------------------------
# Enable MyST extensions
myst_enable_extensions = [
    "colon_fence"
]

# Treat the `mermaid` fence as a Sphinx directive
myst_fence_as_directive = ["mermaid"]

# generate HTML anchors for headings up to level 3 (to enable linking to section headings)
myst_heading_anchors = 3

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_book_theme'
html_logo = "_static/maeser-dark.png"
html_title = f"{project} Documentation"
html_favicon = "_static/maeser-part.png"

html_theme_options = {
    "repository_url": "https://github.com/byu-cpe/Maeser",
    "use_repository_button": True,
    "logo": {
        "image_light": "_static/maeser-light.png",
        "image_dark": "_static/maeser-dark.png",
        "link": "https://github.com/byu-cpe/Maeser",
        "alt_text": html_title
    },
    "collapse_navigation": True,
    "show_nav_level": 0       
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Add all javascript files to be used in the documentation pages
html_js_files = [
    "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js", # Mermaid diagrams
    "js/mermaid-theme-switch.js", # Allows mermaid diagrams to render properly based on current theme
    "js/dynamic-footer-disclaimers.js", # Replaces Author and Copyright disclaimers in the page footer with custom content, allowing hyperlinks to be included
]