# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import datetime
import os
import sys
import nifti_mrs

date = datetime.date.today()

project = 'nifti-mrs'
copyright = f'{date.year}, William Clarke, University of Oxford, Oxford, UK'
author = 'William Clarke'

sys.path.insert(0, os.path.abspath('../src'))

version = nifti_mrs.__version__
release = version


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Show the class level docstring
# (__init__ is documented via the
# special-members flag)
autoclass_content = 'class'


autodoc_default_options = {
    'special-members': False,
    'private-members': False,
    'undoc-members': False,
    'member-order': 'bysource',
}
