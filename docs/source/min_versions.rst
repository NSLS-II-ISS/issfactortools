==================
Supported versions
==================

Python 3.10 and newer are supported. Runtime dependencies and their minimum
versions are declared in ``requirements.txt``: NumPy 1.26, SciPy 1.11,
Matplotlib 3.8, and pyMCR 0.5.1. The optional GUI requires PyQt5 5.15.11.

Pip selects compatible dependency releases for each Python version. CI runs
the regression suite on Python 3.10 through 3.14. Build and development
dependencies are declared in ``pyproject.toml``.
