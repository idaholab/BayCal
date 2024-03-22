# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'BayCal'
copyright = '2024, Congjian Wang'
author = 'Congjian Wang'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.intersphinx',
	'sphinx.ext.autodoc',
	'sphinx.ext.doctest',
	'sphinx.ext.todo',
	"sphinx.ext.autodoc.typehints",
	"sphinx.ext.mathjax",
  "sphinx.ext.autosummary",
	"nbsphinx",  # <- For Jupyter Notebook support
	"sphinx.ext.napoleon",  # <- For Google style docstrings
	"sphinx.ext.imgmath",
	"sphinx.ext.viewcode",
	'autoapi.extension',
  'sphinx_copybutton',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
source_suffix = [".rst", ".md"]
autoapi_dirs = ['../../src']

import sphinx_rtd_theme

html_theme = 'sphinx_rtd_theme'

html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]


# -- Options for Apidoc
# This can be uncommented to "refresh" the api .rst files.
"""
import os

def run_apidoc(app) -> None:
    '''Generage API documentation'''
    import better_apidoc

    better_apidoc.APP = app
    better_apidoc.main([
        'better-apidoc',
        '-t',
        os.path.join('docs', '_templates'),
        '--force',
        '--separate',
        '-o',
        os.path.join('docs', 'modules'),
        os.path.join('dackar'),
    ])


def setup(app) -> None:
    app.connect('builder-inited', run_apidoc)
# """


# def copy_notebooks() -> None:
#     for filename in Path("../examples").glob("*.ipynb"):
#         shutil.copy2(str(filename), "notebooks")


# copy_notebooks()



# -- NBSphinx options
# Do not execute the notebooks when building the docs
nbsphinx_execute = "never"

autodoc_inherit_docstrings = False
autoapi_add_toctree_entry = False
