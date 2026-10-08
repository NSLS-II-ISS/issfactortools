import json

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal
from pymcr.constraints import ConstraintNonneg
from pymcr.regressors import NNLS

from issfactortools.elements.mcrproject import (
    ConstraintSet,
    DataSet,
    MCRProject,
    Optimizer,
    ReferenceSet,
)


def make_dataset():
    return DataSet(
        list(range(6)),
        {"index": list(range(4)), "time": [2, 4, 6, 8]},
        np.arange(24).reshape(6, 4).tolist(),
    )


def test_dataset_masks_and_serialization():
    dataset = make_dataset()
    dataset.set_x_limits(1, 4)
    dataset.set_t_mask([True, False, True, False])
    dataset.set_t("time")
    restored = DataSet.from_dict(json.loads(json.dumps(dataset.to_dict()))["data"])
    assert_array_equal(restored.data, np.arange(24).reshape(6, 4)[1:5, ::2])
    assert_array_equal(restored.x, [1, 2, 3, 4])
    assert_array_equal(restored.t, [2, 6])
    assert restored.t_name == "time"


def test_invalid_masks_leave_dataset_unchanged():
    dataset = make_dataset()
    with pytest.raises(ValueError, match="at least one"):
        dataset.set_x_limits(20, 30)
    assert_array_equal(dataset.x, np.arange(6))
    with pytest.raises(ValueError, match="one-dimensional"):
        dataset.set_t_mask(np.ones((2, 2)))
    assert_array_equal(dataset.t, np.arange(4))


@pytest.mark.parametrize("x,t,data", [([], [1], []), ([1], [1, 2], [[1]]), ([[1]], [1], [[1]])])
def test_invalid_dataset_shapes(x, t, data):
    with pytest.raises(ValueError):
        DataSet(x, {"index": t}, data)


def test_plot_multiple_cuts():
    import matplotlib.pyplot as plt

    dataset = make_dataset()
    _, ax = plt.subplots()
    dataset.plot_data_cut([1, 3], ax=ax)
    assert len(ax.lines) == 2
    assert_array_equal(ax.lines[1].get_ydata(), dataset.data[3])


def test_optimizers_are_independent_with_legacy_alias():
    first, second = Optimizer(), Optimizer()
    assert first.c_optimizer is not second.c_optimizer
    assert first.st_optimizer is not second.st_optimizer
    assert first.st_optimizer is first.st_optmizer
    first.st_optmizer = NNLS()
    assert first.st_optimizer is first.st_optmizer


def test_constraint_serialization_does_not_copy_runtime_objects():
    class Uncopyable:
        def __deepcopy__(self, memo):
            raise AssertionError("runtime object must not be copied")

    constraints = ConstraintSet()
    constraints.append_c_constraint({"object": Uncopyable(), "kwargs": {"values": [1]}})
    serialized = constraints.constraints_without_objects
    serialized[0]["kwargs"]["values"].append(2)
    assert constraints.c_constraints[0]["kwargs"]["values"] == [1]
    assert "object" not in serialized[0]


def test_mcr_recovers_synthetic_mixture():
    x = np.linspace(0, 10, 80)
    spectra = np.column_stack([np.exp(-((x - 3) ** 2)), np.exp(-((x - 7) ** 2))])
    fraction = np.linspace(0.1, 0.9, 12)
    concentrations = np.vstack([fraction, 1 - fraction])
    data = spectra @ concentrations
    dataset = DataSet(x, {"index": list(range(12))}, data)
    references = ReferenceSet()
    for i in range(2):
        references.append_reference(x, spectra[:, i], label=str(i), fixed=True)
    constraints = ConstraintSet()
    constraints.append_c_constraint({"object": ConstraintNonneg()})
    project = MCRProject(
        dataset, references, constraints, Optimizer(c_optimizer=NNLS()), max_iter=10
    )
    project.fit()
    assert_allclose(project.data_fit, data, atol=1e-12)
    assert_allclose(project.c_fit, concentrations, atol=1e-12)
    json.dumps(project.to_dict())
