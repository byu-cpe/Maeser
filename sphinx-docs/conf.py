# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# © 2024 Blaine Freestone, Carson Bush

# This file is part of the Maeser unit test suite.

# Maeser is free software: you can redistribute it and/or modify it under the terms of
# the GNU Lesser General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# Maeser is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# Maeser. If not, see <https://www.gnu.org/licenses/>.


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
    'PIL',
    'pydantic',
    'markdownify',
    'flask',
    'flask-login',
    'flask_login',
    'pytest'
]

# -- Project information -----------------------------------------------------

project = 'Maeser'
copyright = '2024, Carson Bush, Blaine Freestone, Mike Wirthlin, Brent Nelson, Gohaun Manley, Ayden Bales contributors'
author = 'Carson Bush, Blaine Freestone, Mike Wirthlin, Brent Nelson, Gohaun Manley, Ayden Bales contributors'

# The full version, including alpha/beta/rc tags
release = 'alpha'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['myst_parser', 'sphinx.ext.autodoc', 'sphinx.ext.napoleon', 'sphinx.ext.viewcode', 'sphinxcontrib.mermaid']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '.sphinx-venv']

# Enable MyST extensions
myst_enable_extensions = [
    "colon_fence"
]

# Treat the `mermaid` fence as a Sphinx directive
myst_fence_as_directive = ["mermaid"]

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