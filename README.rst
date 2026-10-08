=========================
ISS factor analysis tools
=========================

Linear algebra tools for spectroscopy analysis at the NSLS-II ISS beamline
and beyond. Includes singular value decomposition (SVD), evolving factor
analysis (EFA), multivariate curve resolution (MCR), and an optional Qt interface.

* Free software: 3-clause BSD license
* Python 3.10 or newer

Installation
------------

From a source checkout::

    python -m pip install .

Include the Qt interface with::

    python -m pip install '.[gui]'
    python -m issfactortools.widgets.widget_main

NumPy, SciPy, Matplotlib, and pyMCR are installed automatically. PyQt5 is only
required for the GUI; the numerical tools work without it or ``isstools``.
Dependency minimums are in ``requirements.txt``. Pip selects releases compatible
with the running Python version, including Python 3.10.

Usage
-----

Data matrices use energy points as rows and spectra as columns::

    import numpy as np
    from issfactortools.elements.mcrproject import DataSet
    from issfactortools.elements.svd import compute_efa

    energy = np.linspace(7000, 7200, 100)
    spectra = np.random.default_rng(0).random((100, 20))
    dataset = DataSet(energy, {'index': np.arange(20)}, spectra)
    dataset.compute_svd()
    reconstructed = (dataset.u * dataset.s) @ dataset.v.T
    forward, backward = compute_efa(dataset)

Compatibility notes
-------------------

``doSVD`` now returns compact U and V matrices with ``min(data.shape)`` columns.
The six return values and V orientation are unchanged. Call
``doSVD(data, full_matrices=True)`` for the complete orthonormal bases returned
by previous versions. Compact factors avoid computing and storing unused
null-space vectors for rectangular data.

EFA computes only singular values and reads the selected dataset once per
analysis. Its forward/backward window alignment remains unchanged. Fixed-window
EFA keeps the existing start range ``range(w, nt-w)`` and returns an empty
2D array if no windows fit.

``Optimizer.st_optimizer`` is the corrected attribute name; the original
``st_optmizer`` remains available as an alias. Optimizer instances now own
independent default regressors.

Development and performance checks
----------------------------------

Install development dependencies and run checks::

    python -m pip install -e '.[dev,gui]'
    ruff check issfactortools
    pytest
    python -m build

The GUI tests run offscreen and are skipped when PyQt5 is absent. CI covers
Python 3.10 through 3.14. Build documentation with::

    python -m pip install -e '.[docs]'
    make -C docs html

Compare the numerical routines with the original full-SVD approach::

    OPENBLAS_NUM_THREADS=1 python benchmarks/benchmark_svd.py

The benchmark verifies numerical agreement before reporting median timings and
factor storage. Results depend on matrix shape, BLAS implementation, and hardware.
Package versions are generated from Git metadata at build time with
``setuptools-scm``; unbuilt source checkouts report ``0+unknown``.
