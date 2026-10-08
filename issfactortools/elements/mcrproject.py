import copy

import matplotlib.pyplot as plt
from pymcr.mcr import McrAR
from pymcr.regressors import OLS
import numpy as np

from issfactortools.elements.svd import doSVD


class DataSet:
    def __init__(
        self,
        x,
        t_dict,
        data,
        x_name="energy",
        t_name="index",
        data_name="mu norm",
        x_units="eV",
        t_units="i",
        data_units="",
        name="dataset",
    ):

        self._x = np.asarray(x)
        data = np.asarray(data)
        self._t = np.array(t_dict[t_name])
        self._validate_input(self._x, self._t, data)
        self.t_dict = t_dict
        self._data = data
        self.xmin, self.xmax = 0, 1
        self.set_x_limits(self._x.min(), self._x.max())

        # self.t_mask = np.ones(t.size, dtype=bool)
        self.reset_t_mask()

        self.x_name = x_name
        self.t_name = t_name
        self.data_name = data_name

        self.x_units = x_units
        self.t_units = t_units
        self.data_units = data_units

        self.name = name

    def reset_t_mask(self):
        self.t_mask = np.ones(self._t.size, dtype=bool)

    def _validate_input(self, x, t, data):
        if x.ndim != 1 or t.ndim != 1 or data.ndim != 2:
            raise ValueError("x and t must be one-dimensional and data two-dimensional")
        if not x.size or not t.size:
            raise ValueError("x and t must not be empty")
        nx, nt = data.shape
        sizes_match = (nx == x.size) and (nt == t.size)
        if not sizes_match:
            raise ValueError("x, t, and data sizes/shapes do not match")

    def set_x_limits(self, xmin, xmax):
        mask = (self._x >= xmin) & (self._x <= xmax)
        if not mask.any():
            raise ValueError("x limits must include at least one data point")
        self.x_mask = mask
        self.xmin = self.x.min().item()
        self.xmax = self.x.max().item()

    def set_t_mask(self, t_mask):
        t_mask = np.asarray(t_mask, dtype=bool)
        if t_mask.shape != self._t.shape:
            raise ValueError("t_mask must be one-dimensional and the same size as t")
        self.t_mask = t_mask.copy()

    def set_t(self, key):
        t = np.asarray(self.t_dict[key])
        self._validate_input(self._x, t, self._data)
        self._t = t
        self.t_name = key
        # self.reset_t_mask()

    @property
    def data(self):
        # return self._data[self.x_mask, self.t_mask]
        return self._data[np.ix_(self.x_mask, self.t_mask)]

    @property
    def x(self):
        return self._x[self.x_mask]

    @property
    def t(self):
        return self._t[self.t_mask]

    @property
    def name_list(self):
        return self.t_dict["name"]

    @property
    def is_included_list(self):
        return self.t_mask.tolist()

    def compute_svd(self):
        self.u, self.s, self.v, self.lra_chisq, self.ac_u, self.ac_v = self._compute_svd(self.data)

    def _compute_svd(self, data):
        return doSVD(data)

    # def compute_efa(self):
    #     nx, nt = self.data.shape
    #     ss_forward = np.zeros((nt, nt-1))
    #     for i in range(1, nt):
    #         _u, _s, _v, _, _, _ = self.compute_svd(self.data[:, :i])
    #         n_i = _s.size
    #         ss[:n_i, i - 1] = _s
    #     return ss

    def plot_data(self, ax=None):
        if ax is None:
            _, ax = plt.subplots(1)
        x = self.x
        # t = self.t
        data = self.data
        x_label = f"{self.x_name}, {self.x_units}"
        # t_label = f"{self.t_name}, {self.t_units}"
        data_label = f"{self.data_name}, {self.data_units}"
        ax.plot(x, data)
        ax.set_xlabel(x_label)
        ax.set_ylabel(data_label)
        ax.title.set_text("Data")
        _ymin, _ymax = ax.get_ylim()
        _yspan = _ymax - _ymin
        ymax = _ymax + 0.05 * _yspan
        ymin = _ymin - 0.05 * _yspan
        ax.set_ylim(top=ymax, bottom=ymin)

    def plot_data_cut(self, cut_indices, ax=None):
        if ax is None:
            _, ax = plt.subplots()
        # x = self.x
        t = self.t
        cuts = self.data[cut_indices, :]
        # x_label = f"{self.x_name}, {self.x_units}"
        t_label = f"{self.t_name}, {self.t_units}"
        data_label = f"{self.data_name}, {self.data_units}"
        ax.plot(t, cuts.T)
        ax.set_xlabel(t_label)
        ax.set_ylabel(data_label)
        ax.title.set_text("Data")
        _ymin, _ymax = ax.get_ylim()
        _yspan = _ymax - _ymin
        ymax = _ymax + 0.05 * _yspan
        ymin = _ymin - 0.05 * _yspan
        ax.set_ylim(top=ymax, bottom=ymin)

    def plot_svd(self, figure_svd=None, figure_stat=None, n_cmp_show=3, n_val_show=25):
        if figure_svd is None:
            figure_svd = plt.figure()
        if figure_stat is None:
            figure_stat = plt.figure()
        self.compute_svd()

        ax_u = figure_svd.add_subplot(2, 1, 1)
        ax_v = figure_svd.add_subplot(2, 1, 2)

        ax_s = figure_stat.add_subplot(2, 1, 1)
        ax_ac = figure_stat.add_subplot(2, 1, 2)

        ax_u.plot(self.x, self.u[:, :n_cmp_show])
        ax_u.set_xlabel(f"{self.x_name}, {self.x_units}")
        ax_u.legend([str(i + 1) for i in range(n_cmp_show)])

        ax_v.plot(self.t, self.v[:, :n_cmp_show])
        ax_v.set_xlabel(f"{self.t_name}, {self.t_units}")
        ax_v.legend([str(i + 1) for i in range(n_cmp_show)])

        ax_s.semilogy(self.s[:n_val_show], "k.-", label="Singular values")
        ax_s.semilogy(self.lra_chisq[:n_val_show], "bs-", label="chisq")
        ax_s.legend()
        ax_s.set_xlabel("component index")

        ax_ac.plot(self.ac_u[:n_val_show], "k.-", label="AC$_U$")
        ax_ac.plot(self.ac_v[:n_val_show], "r.-", label="AC$_V$")
        ax_ac.legend()
        ax_ac.set_xlabel("component index")

    def to_dict(self):
        data_dict = {
            "x": self._x.tolist(),
            "t_dict": {key: np.asarray(value).tolist() for key, value in self.t_dict.items()},
            "data": self._data.tolist(),
            "x_name": self.x_name,
            "t_name": self.t_name,
            "data_name": self.data_name,
            "x_units": self.x_units,
            "t_units": self.t_units,
            "data_units": self.data_units,
            "name": self.name,
            "xmin": self.xmin,
            "xmax": self.xmax,
            "t_mask": self.t_mask.tolist(),
        }
        return {"kind": "dataset", "data": data_dict}

    # def to_json(self, filename):
    #     data_dict = self.to_dict()
    #     with open(filename, 'w') as f:
    #         f.write(json.dumps(data_dict))

    @classmethod
    def from_dict(cls, data_dict):
        # data_dict = input_dict['data']
        output = cls(
            np.array(data_dict["x"]),
            data_dict["t_dict"],
            np.array(data_dict["data"]),
            x_name=data_dict["x_name"],
            t_name=data_dict["t_name"],
            data_name=data_dict["data_name"],
            x_units=data_dict["x_units"],
            t_units=data_dict["t_units"],
            data_units=data_dict["data_units"],
            name=data_dict["name"],
        )
        output.set_t_mask(np.array(data_dict["t_mask"]))
        output.set_x_limits(data_dict["xmin"], data_dict["xmax"])
        return output

    # @classmethod
    # def from_json(cls, filename):
    #     with open(filename, 'r') as f:
    #         data_dict = json.loads(f.read())
    #     return cls.from_dict(data_dict)

    # plot_svd_results(self.x, self.t, self.u, self.s, self.v, self.lra_chisq, self.ac_u, self.ac_v, figure_svd, figure_stat, n_cmp_show=n_cmp_show, n_val_show=n_val_show)


class ReferenceSet:
    def __init__(self, name="Reference Set"):
        self.reference_dict = {}
        self.name = name

    def append_reference(self, x, data, label: str = "Reference", fixed: bool = False):
        self.validate_reference(x, data, label)
        _d = {"x": x, "data": data, "fixed": fixed}
        # self.reference_dict = {label : _d}
        self.reference_dict[label] = _d

    def validate_reference(self, x, data, label):
        shape_match = len(data.shape) == 1
        if not shape_match:
            raise Exception(
                f"{label} Reference data shape mismatch: data.shape should be ({data.size}, );  currently is {data.shape}"
            )

        size_match = data.size == x.size
        if not size_match:
            raise Exception(
                f"{label} Reference data size mismatch: data.size should be == x.size; currently: data.size={data.size} and x.size={x.size}"
            )

        label_match = label in self.labels
        if label_match:
            raise KeyError(f"Provided labels must be unique. {label} already exists")

    @property
    def labels(self):
        return list(self.reference_dict.keys())

    def to_dict(self):
        data_dict = {
            label: {
                key: value.tolist() if isinstance(value, np.ndarray) else copy.deepcopy(value)
                for key, value in reference.items()
            }
            for label, reference in self.reference_dict.items()
        }
        return {"kind": "refset", "data": data_dict, "name": self.name}

    @classmethod
    def from_dict(cls, input_dict, name="Reference Set"):
        data_dict = input_dict
        output = cls(name=name)
        for label, item in data_dict.items():
            output.append_reference(
                np.array(item["x"]), np.array(item["data"]), label=label, fixed=item["fixed"]
            )
        return output


class ConstraintSet:
    def __init__(self):
        self.c_constraints = []
        self.st_constraints = []

    def append_c_constraint(self, c_constraint):
        self.c_constraints.append(c_constraint)

    def append_st_constraint(self, st_constraint):
        self.st_constraints.append(st_constraint)

    @property
    def constraints(self):
        return self.c_constraints + self.st_constraints

    @property
    def constraints_without_objects(self):
        return [
            copy.deepcopy({key: value for key, value in constraint.items() if key != "object"})
            for constraint in self.constraints
        ]

    @property
    def c_constraints_obj(self):
        return [element["object"] for element in self.c_constraints]

    @property
    def st_constraints_obj(self):
        return [element["object"] for element in self.st_constraints]


# def to_dict(self):
#     output = []
#     for _constraint in (self.c_constraints + self.st_constraints):
#         constraint = copy.deepcopy(_constraint)
#         constraint.pop('object')
#         output.append(constraint)
#     return output


class Optimizer:
    def __init__(self, c_optimizer=None, st_optimizer=None):
        self.c_optimizer = OLS() if c_optimizer is None else c_optimizer
        self.st_optimizer = OLS() if st_optimizer is None else st_optimizer

    @property
    def st_optmizer(self):
        """Backward-compatible alias for the original misspelled attribute."""
        return self.st_optimizer

    @st_optmizer.setter
    def st_optmizer(self, value):
        self.st_optimizer = value


class MCRProject:
    def __init__(
        self,
        dataset: DataSet,
        refset: ReferenceSet,
        conset: ConstraintSet,
        optimizer: Optimizer,
        max_iter: int = 1000,
        tol_increase: float = 1e-3,
        name: str = "MCR project",
    ):

        self.dataset = dataset
        self.refset = refset
        self.conset = conset
        self.optimizer = optimizer
        self.max_iter = max_iter
        self.tol_increase = tol_increase
        self.name = name

        self._interp_refset()

        self.mcr = McrAR(
            c_regr=self.optimizer.c_optimizer,
            st_regr=self.optimizer.st_optimizer,
            c_constraints=self.conset.c_constraints_obj,
            st_constraints=self.conset.st_constraints_obj,
            max_iter=self.max_iter,
            tol_increase=tol_increase,
        )

    def _check_refset_limits(self):
        bad_labels = ""
        for label in self.refset.labels:
            ref_dict = self.refset.reference_dict[label]
            if not (
                (ref_dict["x"].min() <= self.dataset.xmin)
                and (ref_dict["x"].max() >= self.dataset.xmax)
            ):
                bad_labels += label + " "
        if len(bad_labels) > 0:
            msg = bad_labels + "Reference(s) energy grid does not cover experimental energy grid"
            assert len(bad_labels) == 0, msg

    def _interp_refset(self):
        self._check_refset_limits()
        x_interp = self.dataset.x
        self.data_ref = np.zeros((x_interp.size, len(self.refset.labels)))
        self.fix_ref = []
        for i, label in enumerate(self.refset.labels):
            ref_dict = self.refset.reference_dict[label]
            x = ref_dict["x"]
            y = ref_dict["data"]
            self.data_ref[:, i] = np.interp(x_interp, x, y)
            if ref_dict["fixed"]:
                self.fix_ref.append(i)
        if len(self.fix_ref) == 0:
            self.fix_ref = None

    def fit(self):
        self.mcr.fit(
            self.dataset.data.T,
            ST=self.data_ref.T,
            # c_fix=[],
            st_fix=self.fix_ref,
        )

        self.data_ref_fit = self.mcr.ST_opt_.T
        self.c_fit = self.mcr.C_opt_.T
        self.data_fit = self.data_ref_fit @ self.c_fit

    def plot_results(self, fig=None, offset=0.5):
        if fig is None:
            fig = plt.figure()
        plt.figure(fig.number)
        plt.subplot(121)
        plt.plot(self.dataset.x, self.dataset.data, "k")
        plt.plot(self.dataset.x, self.data_fit, "r")
        plt.title(f"Data Fit ({self.dataset.name})")

        plt.subplot(222)
        n_curves = self.data_ref.shape[1]
        for i in range(n_curves):
            plt.plot(self.dataset.x, self.data_ref[:, i] - i * offset, "k")
            plt.plot(self.dataset.x, self.data_ref_fit[:, i] - i * offset)
            plt.text(
                self.dataset.x[0],
                self.data_ref[0, i] - i * offset + 0.1,
                self.refset.labels[i],
                va="center",
                ha="center",
            )
        plt.title(f"Refined References ({self.refset.name})")

        plt.subplot(224)
        for i in range(n_curves):
            plt.plot(self.dataset.t, self.c_fit[i, :], label=self.refset.labels[i])
        plt.plot(self.dataset.t, np.sum(self.c_fit, axis=0), "k:", label="total")
        plt.title("Refined concentrations")
        plt.legend()
        plt.show()

    def to_dict(self):
        output = {}
        output["dataset"] = self.dataset.to_dict()
        output["refset"] = self.refset.to_dict()
        output["conset"] = self.conset.constraints_without_objects
        if hasattr(self, "data_ref_fit"):
            output["data_ref_fit"] = {
                "data_ref_fit": self.data_ref_fit.tolist(),
                "x": self.dataset.x.tolist(),
            }
        if hasattr(self, "data_fit"):
            output["data_fit"] = {"data_fit": self.data_fit.tolist(), "x": self.dataset.x.tolist()}
        if hasattr(self, "c_fit"):
            output["c_fit"] = {"c_fit": self.c_fit.tolist(), "t": self.dataset.t.tolist()}
        output["max_iter"] = self.max_iter
        output["tol_increase"] = self.tol_increase
        output["name"] = self.name
        return {"kind": "mcrproj", "data": output}
