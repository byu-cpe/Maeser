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
# sys.path.insert(0, os.path.abspath('../maeser'))
# sys.path.insert(0, os.path.abspath('../tests'))
sys.path.insert(0, os.path.abspath('/lib/python3.10/site-packages/'))
sys.path.insert(0, os.path.abspath('../.venv/lib/python3.10/site-packages/'))

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
]

# -- Project information -----------------------------------------------------

project = 'Maeser'
copyright = '2024, Carson Bush, Blaine Freestone, Mike Wirthlin, Brent Nelson, contributors'
author = 'Carson Bush, Blaine Freestone, Mike Wirthlin, Brent Nelson, contributors'

# The full version, including alpha/beta/rc tags
release = 'alpha'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['myst_parser', 'sphinx.ext.autodoc', 'sphinx.ext.napoleon']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


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
    }
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']