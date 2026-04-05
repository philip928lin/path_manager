# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Make the package importable so autodoc can inspect it
sys.path.insert(0, os.path.abspath('../src'))

# -- Project information -------------------------------------------------------

project = 'PathNavigator'
copyright = '2024, Chung-Yi Lin'
author = 'Chung-Yi Lin'

try:
    from importlib.metadata import version as _pkg_version
    release = _pkg_version('pathnavigator')
except Exception:
    release = '0.6.3'
version = '.'.join(release.split('.')[:2])  # short X.Y version

# -- General configuration -----------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',          # core: pull docstrings from source
    'sphinx.ext.autosummary',      # generate summary tables
    'sphinx.ext.napoleon',         # NumPy / Google docstring support
    'sphinx.ext.viewcode',         # add [source] links to every member
    'sphinx.ext.intersphinx',      # cross-link to Python stdlib docs
    'sphinx_autodoc_typehints',    # render PEP 484 type hints
    'sphinx_copybutton',           # copy-to-clipboard button on code blocks
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Autodoc -------------------------------------------------------------------

autodoc_default_options = {
    'members': True,
    'undoc-members': False,    # skip members without docstrings
    'private-members': False,  # skip _private and __dunder__ members
    'show-inheritance': True,
    'member-order': 'bysource',
}
autodoc_typehints = 'description'   # put type hints in the Parameters block
autodoc_typehints_format = 'short'  # use short names (Path not pathlib.Path)
autoclass_content = 'both'          # include both class and __init__ docstrings

# -- Napoleon (NumPy docstring style) ------------------------------------------

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True

# -- Intersphinx ---------------------------------------------------------------

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

# -- Copy-button ---------------------------------------------------------------

copybutton_prompt_text = r'>>> |\.\.\. |\$ '
copybutton_prompt_is_regexp = True

# -- HTML output (Furo theme) --------------------------------------------------

html_theme = 'furo'
html_title = f'PathNavigator {release}'
html_static_path = ['_static']

html_theme_options = {
    'sidebar_hide_name': False,
    'navigation_with_keys': True,
    'light_css_variables': {
        'color-brand-primary': '#1A6496',
        'color-brand-content': '#1A6496',
    },
    'dark_css_variables': {
        'color-brand-primary': '#4DA8D1',
        'color-brand-content': '#4DA8D1',
    },
    'footer_icons': [
        {
            'name': 'GitHub',
            'url': 'https://github.com/philip928lin/PathNavigator',
            'html': (
                '<svg stroke="currentColor" fill="currentColor" stroke-width="0" '
                'viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 '
                '3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37'
                '-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 '
                '1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64'
                '-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 '
                '2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82'
                '.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95'
                '.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013'
                ' 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path></svg>'
            ),
            'class': '',
        },
    ],
}
