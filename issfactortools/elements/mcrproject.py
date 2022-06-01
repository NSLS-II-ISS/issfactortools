import copy

import matplotlib.pyplot as plt
from pymcr.mcr import McrAR
import numpy as np
import json

from issfactortools.elements.svd import doSVD, plot_svd_results


class DataSet:

    def __init__(self, x, t_dict, data,
                 x_name='energy', t_name='index', data_name='mu norm',
                 x_units='eV', t_units='i', data_units='',
                 name='dataset'):

        # self._validate_input(x, t, data)
        self._x = x
        self._t = np.array(t_dict[t_name])
        self._validate_input(self._x, self._t, data)
        self.t_dict = t_dict
        self._data = data
        self.xmin, self.xmax = 0, 1
        self.set_x_limits(x.min(), x.max())

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
        nx, nt = data.shape
        sizes_match = (nx == x.size) and (nt == t.size)
        if not sizes_match:
            raise Exception('x, t, and data sizes/shapes do not match')

    def set_x_limits(self, xmin, xmax):
        self.x_mask = (self._x >= xmin) & (self._x <= xmax)
        self.xmin = self.x.min()
        self.xmax = self.x.max()

    def set_t_mask(self, t_mask):
        if t_mask.size == self._t.size:
            self.t_mask = t_mask
        else:
            raise Exception('Error: t_mask must be the same size as t')

    def set_t(self, key):
        self._t = np.array(self.t_dict[key])
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
        return self.t_dict['name']

    @property
    def is_included_list(self):
        return self.t_mask.tolist()

    def compute_svd(self):
        self.u, self.s, self.v, self.lra_chisq, self.ac_u, self.ac_v = doSVD(self.data)


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
            _, ax = plt.subplots(1, 1, 1)
        #x = self.x
        t = self.t
        cuts = self.data[cut_indices, :]
        #x_label = f"{self.x_name}, {self.x_units}"
        t_label = f"{self.t_name}, {self.t_units}"
        data_label = f"{self.data_name}, {self.data_units}"
        ax.plot(t, cuts)
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

        ax_s.semilogy(self.s[:n_val_show], 'k.-', label='Singular values')
        ax_s.semilogy(self.lra_chisq[:n_val_show], 'bs-', label='chisq')
        ax_s.legend()
        ax_s.set_xlabel(f"component index")

        ax_ac.plot(self.ac_u[:n_val_show], 'k.-', label='AC$_U$')
        ax_ac.plot(self.ac_v[:n_val_show], 'r.-', label='AC$_V$')
        ax_ac.legend()
        ax_ac.set_xlabel(f"component index")

    def to_dict(self):
        return {'x' : self._x.tolist(),
                't_dict' : self.t_dict,
                'data' : self._data.tolist(),
                'x_name' : self.x_name,
                't_name' : self.t_name,
                'data_name' : self.data_name,
                'x_units' : self.x_units,
                't_units' : self.t_units,
                'data_units' : self.data_units,
                'name' : self.name,
                'xmin' : self.xmin,
                'xmax' : self.xmax,
                't_mask' : self.t_mask.tolist()}

    # def to_json(self, filename):
    #     data_dict = self.to_dict()
    #     with open(filename, 'w') as f:
    #         f.write(json.dumps(data_dict))

    @classmethod
    def from_dict(cls, data_dict):
        output = cls(np.array(data_dict['x']), data_dict['t_dict'], np.array(data_dict['data']),
                     x_name=data_dict['x_name'], t_name=data_dict['t_name'], data_name=data_dict['data_name'],
                     x_units=data_dict['x_units'], t_units=data_dict['t_units'], data_units=data_dict['data_units'],
                     name=data_dict['name'])
        output.set_t_mask(np.array(data_dict['t_mask']))
        output.set_x_limits(data_dict['xmin'], data_dict['xmax'])
        return output

    # @classmethod
    # def from_json(cls, filename):
    #     with open(filename, 'r') as f:
    #         data_dict = json.loads(f.read())
    #     return cls.from_dict(data_dict)

        # plot_svd_results(self.x, self.t, self.u, self.s, self.v, self.lra_chisq, self.ac_u, self.ac_v, figure_svd, figure_stat, n_cmp_show=n_cmp_show, n_val_show=n_val_show)

class ReferenceSet:
    def __init__(self):
        self.reference_dict = {}

    def append_reference(self, x, data, label:str = "Reference", fixed:bool = False):
        self.validate_reference(x, data, label)
        _d = {'x' : x, 'data': data, 'fixed' : fixed}
        #self.reference_dict = {label : _d}
        self.reference_dict[label] = _d

    def validate_reference(self, x, data, label):
        shape_match = (len(data.shape) == 1)
        if not shape_match:
            raise Exception(f'{label} Reference data shape mismatch: data.shape should be ({data.size}, );  currently is {data.shape}')

        size_match = (data.size == x.size)
        if not size_match:
            raise Exception(f'{label} Reference data size mismatch: data.size should be == x.size; currently: data.size={data.size} and x.size={x.size}')

        label_match = (label in self.labels)
        if label_match:
            raise KeyError(f'Provided labels must be unique. {label} already exists')

    @property
    def labels(self):
        return list(self.reference_dict.keys())

    def to_dict(self):
        data_dict = copy.deepcopy(self.reference_dict)
        for label, val in data_dict.items():
            for key, arr in val.items():
                if type(arr) == np.ndarray:
                    val[key] = arr.tolist()
        return data_dict

    @classmethod
    def from_dict(cls, data_dict):
        output = cls()
        for label, item in data_dict.items():
            output.append_reference(np.array(item['x']), np.array(item['data']), label=label, fixed=item['fixed'])
        return output


class ConstraintSet:
    def __init__(self):
        self.c_constraints = []
        self.st_constraints = []

    def append_c_constraint(self, c_constraint):
        self.c_constraints.append(c_constraint)

    def append_st_constraint(self, st_constraint):
        self.st_constraints.append(st_constraint)


from pymcr.regressors import OLS, NNLS
class Optimizer:
    def __init__(self, c_optimizer=OLS(), st_optimizer=OLS()):
        self.c_optimizer = c_optimizer
        self.st_optmizer = st_optimizer


class MCRProject:

    def __init__(self,
                 dataset : DataSet,
                 refset : ReferenceSet,
                 conset : ConstraintSet,
                 optimizer : Optimizer,
                 max_iter : int = 1000):

        self.dataset = dataset
        self.refset = refset
        self.conset = conset
        self.optimizer = optimizer
        self.max_iter = max_iter

        self._interp_refset()

        self.mcr = McrAR(c_regr=self.optimizer.c_optimizer,
                         st_regr=self.optimizer.st_optmizer,
                         c_constraints=self.conset.c_constraints,
                         st_constraints=self.conset.st_constraints,
                         max_iter=self.max_iter)

    def _check_refset_limits(self):
        bad_labels = ''
        for label in self.refset.labels:
            ref_dict = self.refset.reference_dict[label]
            if not ((ref_dict['x'].min() <= self.dataset.xmin) and
                    (ref_dict['x'].max() >= self.dataset.xmax)):
                bad_labels += (label + ' ')
        if len(bad_labels) > 0:
            msg = bad_labels + 'Reference(s) energy grid does not cover experimental energy grid'
            assert len(bad_labels) == 0, msg

    def _interp_refset(self):
        self._check_refset_limits()
        x_interp = self.dataset.x
        self.data_ref = np.zeros((x_interp.size, len(self.refset.labels)))
        self.fix_ref = []
        for i, label in enumerate(self.refset.labels):
            ref_dict = self.refset.reference_dict[label]
            x = ref_dict['x']
            y = ref_dict['data']
            self.data_ref[:, i] = np.interp(x_interp, x, y)
            if ref_dict['fixed']:
                self.fix_ref.append(i)
        if len(self.fix_ref) == 0:
            self.fix_ref = None


    def fit(self):
        self.mcr.fit(self.dataset.data.T, ST=self.data_ref.T,
                     # c_fix=[],
                     st_fix=self.fix_ref)

        self.data_ref_fit = self.mcr.ST_opt_.T
        self.c_fit = self.mcr.C_opt_.T
        self.data_fit = (self.data_ref_fit @ self.c_fit)


    def plot_results(self, fig=None):
        if fig is None:
            fig = plt.figure()
        plt.figure(fig.number)
        plt.subplot(121)
        plt.plot(self.dataset.x, self.dataset.data, 'k')
        plt.plot(self.dataset.x, self.data_fit, 'r')
        plt.title('Data Fit')

        plt.subplot(222)
        plt.plot(self.dataset.x, self.data_ref, 'k')
        plt.plot(self.dataset.x, self.data_ref_fit, 'r')
        plt.title('Refined References')

        plt.subplot(224)
        plt.plot(self.dataset.t, self.c_fit.T)
        plt.title('Refined concentrations')
        plt.show()


















