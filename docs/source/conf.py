# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

def get_version():
    version = 'develop'
    try:
        # readthedocs installs the package first
        import sanotehu
        version = sanotehu.__version__
    except ImportError:
        import subprocess
        result = subprocess.run(['git', 'describe'], capture_output=True)
        if result.returncode == 0:
            version = result.stdout.decode('utf-8').strip()
    return version


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'sanotehu'
copyright = '2026, Lourens Veen'
author = 'Lourens Veen'
version = get_version()
release = get_version()


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
