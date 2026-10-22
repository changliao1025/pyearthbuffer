# PyEarthBuffer Documentation

This directory contains the Sphinx documentation for PyEarthBuffer, following
the documentation layout used by other PyEarthSuite projects.

## Directory Layout

```text
docs/
├── Makefile
├── make.bat
├── requirements.txt
├── README.md
└── source/
    ├── conf.py
    ├── index.rst
    ├── getting-started.rst
    ├── geometry-api.rst
    ├── file-api.rst
    ├── architecture.md
    ├── raster.rst
    ├── faq.rst
    ├── support.rst
    ├── authors.rst
    └── contribution.rst
```

## Build the documentation locally

```bash
python -m pip install -r docs/requirements.txt
cd docs
make html
```

Open `docs/_build/html/index.html` to browse the generated site. Read the Docs
uses the repository-level `.readthedocs.yaml` configuration to build and publish
the documentation.
