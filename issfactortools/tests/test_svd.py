from types import SimpleNamespace

import matplotlib.pyplot as plt
import numpy as np
import pytest
from numpy.testing import assert_allclose

from issfactortools.elements.svd import (
    _getAutocorrelation,
    _get_lra_chisq,
    compute_efa,
    compute_fwefa,
    doSVD,
    getAutocorrelation,
    plot_data,
)


@pytest.mark.parametrize("shape", [(40, 7), (7, 40), (8, 8), (1, 5)])
def test_svd_reconstruction_and_diagnostics(shape):
    data = np.random.default_rng(13).normal(size=shape)
    u, s, v, chisq, ac_u, ac_v = doSVD(data)
    rank = min(shape)
    assert u.shape == (shape[0], rank)
    assert v.shape == (shape[1], rank)
    assert_allclose((u * s) @ v.T, data, atol=1e-13)
    for n in range(1, rank + 1):
        residual = data - (u[:, :n] * s[:n]) @ v[:, :n].T
        assert_allclose(chisq[n - 1], np.sum(residual**2), atol=1e-24)
    assert_allclose(ac_u, np.sum(u[1:] * u[:-1], axis=0))
    assert_allclose(ac_v, np.sum(v[1:] * v[:-1], axis=0))


def test_full_svd_compatibility():
    data = np.arange(24).reshape(8, 3)
    u, s, v, *_ = doSVD(data, full_matrices=True)
    assert u.shape == (8, 8)
    assert v.shape == (3, 3)
    assert_allclose((u[:, :3] * s) @ v.T, data, atol=1e-13)


@pytest.mark.parametrize("lag", [1, 2, 6, 9])
def test_autocorrelation_matches_column_sums(lag):
    data = np.random.default_rng(4).normal(size=(6, 9))
    expected = [sum(col[lag:] * col[:-lag]) for col in data.T]
    assert_allclose(_getAutocorrelation(data, lag), expected)


@pytest.mark.parametrize("lag", [0, -1, 1.5])
def test_invalid_autocorrelation_lag(lag):
    with pytest.raises(ValueError, match="positive integer"):
        _getAutocorrelation(np.ones((4, 3)), lag)


def test_autocorrelation_plot():
    _, ax = plt.subplots()
    getAutocorrelation(np.eye(4), fig=ax)
    assert len(ax.lines) == 2
    assert_allclose(ax.lines[0].get_ydata(), np.zeros(4))


@pytest.mark.parametrize("yscale", [False, True, "log", "linear"])
def test_plot_respects_coordinates_limits_and_no_duplicates(yscale):
    x = np.arange(5) + 100
    data = np.arange(10).reshape(5, 2) + 1
    ax = plot_data(x, data, limits=3, yscale=yscale)
    assert len(ax.lines) == 2
    for i, line in enumerate(ax.lines):
        assert_allclose(line.get_xdata(), x[:3])
        assert_allclose(line.get_ydata(), data[:3, i])
    assert ax.get_yscale() == ("log" if yscale in (True, "log") else "linear")


@pytest.mark.parametrize("shape", [(12, 7), (3, 7), (4, 1)])
def test_efa_preserves_legacy_windows(shape):
    data = np.random.default_rng(3).normal(size=shape)
    forward, backward = compute_efa(SimpleNamespace(data=data))
    assert forward.shape == backward.shape == (shape[1], shape[1] - 1)
    for i in range(1, shape[1]):
        expected_f = np.linalg.svd(data[:, :i])[1]
        expected_b = np.linalg.svd(data[:, -i - 1 :])[1]
        assert_allclose(forward[:, i - 1], np.pad(expected_f, (0, shape[1] - len(expected_f))))
        assert_allclose(backward[:, -i], np.pad(expected_b, (0, shape[1] - len(expected_b))))


@pytest.mark.parametrize("w", [1, 3, 5, 20])
def test_fwefa_preserves_windows_and_handles_empty_result(w):
    data = np.random.default_rng(5).normal(size=(4, 10))
    result = compute_fwefa(SimpleNamespace(data=data), w=w)
    starts = range(w, 10 - w)
    assert result.shape == (len(starts), min(4, w))
    for row, start in enumerate(starts):
        assert_allclose(result[row], np.linalg.svd(data[:, start : start + w])[1])


@pytest.mark.parametrize("w", [0, -2, 1.5])
def test_fwefa_invalid_window(w):
    with pytest.raises(ValueError, match="positive integer"):
        compute_fwefa(SimpleNamespace(data=np.ones((4, 10))), w)


@pytest.mark.parametrize("compute", [compute_efa, compute_fwefa])
def test_efa_reads_selected_data_once(compute):
    class CountingData:
        reads = 0

        @property
        def data(self):
            self.reads += 1
            return np.ones((4, 12))

    dataset = CountingData()
    compute(dataset)
    assert dataset.reads == 1


def test_empty_rank_diagnostics():
    assert _get_lra_chisq(np.array([])).shape == (0,)


@pytest.mark.parametrize("perturb", [0, 0.1])
def test_lra_matches_explicit_reconstruction(perturb):
    from issfactortools.elements.svd import LRA

    data = np.random.default_rng(6).normal(size=(20, 5))
    u, s, vh = np.linalg.svd(data, full_matrices=False)
    u = u + perturb  # Verify actual residuals even when the factors are approximate.
    tails, residuals = LRA(u, s, vh, 6, data)
    for rank in range(1, 6):
        residual = data - (u[:, :rank] * s[:rank]) @ vh[:rank]
        assert_allclose(residuals[rank - 1], np.sum(residual**2), atol=1e-24)
        assert_allclose(tails[rank - 1], np.sum(s[rank:] ** 2))


def test_creategraph_uses_supplied_figure_without_duplicate_lines(monkeypatch):
    from issfactortools.elements.svd import creategraph

    monkeypatch.setattr(plt, "show", lambda: None)
    fig = plt.figure()
    creategraph(np.ones((5, 3)), "title", "x", "y", 2, "c", "column", fig=fig)
    assert len(fig.axes[0].lines) == 2
    assert fig.axes[0].get_title() == "title"
