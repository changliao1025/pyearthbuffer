"""Sphinx configuration for PyEarthBuffer documentation."""

import os
import sys

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

PACKAGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, PACKAGE_ROOT)


def get_version():
    """Read the package version from pyproject.toml."""
    if tomllib is None:
        return "0.1.0"

    pyproject_path = os.path.join(PACKAGE_ROOT, "pyproject.toml")
    with open(pyproject_path, "rb") as pyproject_file:
        project_data = tomllib.load(pyproject_file)
    return project_data["project"]["version"]


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "myst_parser",
]

autodoc_mock_imports = [
    "osgeo",
    "ogr",
    "osr",
    "pyearth",
    "numpy",
    "scipy",
    "geographiclib",
    "cartopy",
    "matplotlib",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "gdal": ("https://gdal.org/", None),
    "pyearth": ("https://pyearth.readthedocs.io/en/latest/", None),
}

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
master_doc = "index"

project = "pyearthbuffer"
copyright = "2026, Battelle Memorial Institute"
author = "Chang Liao"
version = get_version()
release = version

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
templates_path = ["_templates"]
pygments_style = "sphinx"

html_theme = "sphinx_rtd_theme"
html_static_path = []
html_theme_options = {
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}
