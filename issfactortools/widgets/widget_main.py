import re
import sys
import numpy as np
import pkg_resources
import math

from PyQt5 import uic, QtGui, QtCore, QtWidgets
from PyQt5.QtCore import QThread, QSettings

from issfactortools.widgets import widget_data_overview, widget_mcr_overview
from issfactortools.elements.mcrproject import DataSet, ReferenceSet, ConstraintSet

ui_path = pkg_resources.resource_filename('issfactortools', 'ui/ui_main.ui')



class FactorAnalysisGUI(*uic.loadUiType(ui_path)):

    progress_sig = QtCore.pyqtSignal()

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.parent = parent

        self.push_import_dataset.clicked.connect(self.import_dataset)
        self.model_datasets = QtGui.QStandardItemModel(self) # model that is used to show listview of datasets
        self.model_references = QtGui.QStandardItemModel(self)  # model that is used to show listview of references
        self.model_constraints = QtGui.QStandardItemModel(self)  # model that is used to show listview of constraints

        #
        # self.widget_data_overview = widget_data_overview.UIDataOverview()
        # self.layout_data_overview.addWidget(self.widget_data_overview)
        #
        # self.widget_mcr_overview = widget_mcr_overview.UIDataOverview()
        # self.layout_mcr_analysis.addWidget(self.widget_mcr_overview)

    def _append_item_to_model(self, model, item):
        parent = model.invisibleRootItem()
        parent.appendRow(item)

    def _make_item(self, name):
        item = QtGui.QStandardItem(name)
        item.setDropEnabled(False)
        item.setCheckable(True)
        item.setEditable(False)
        return item

    def _create_dataset(self, x, t, data, name='DataSet'):
        item = self._make_item(name)
        item.item_type = 'DataSet'
        item.dataset = DataSet(x, t, data, name)
        self._append_item_to_model(self.model_datasets, item)
        self.listView_datasets.setModel(self.model_datasets)

    # the two methods below are placeholders:

    # def _create_reference_set(self, name='ReferenceSet'):
    #     item = self._make_item(name)
    #     item.item_type = 'ReferenceSet'
    #     item.references = ReferenceSet()
    #     self._append_item_to_model(self.model_references, item)
    #     self.listView_references.setModel(self.model_references)
    #
    # def _create_constraint_set(self, name='ConstraintSet'):
    #     item = self._make_item(name)
    #     item.item_type = 'ConstraintSet'
    #     item.constraints = ConstraintSet()
    #     self._append_item_to_model(self.model_constraints, item)
    #     self.listView_constraints.setModel(self.model_constraints)


    def import_dataset(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(directory='/nsls2/xf08id/Sandbox',
                                                         filter='*.xas', parent=self)[0]
        filedata = np.genfromtxt(filename)
        x = filedata[:, 0]
        data = filedata[:, 1:]
        t = np.arange(data.shape[1])
        self._create_dataset(x, t, data, name=filename)







def main_show():
    xfactor_gui = FactorAnalysisGUI()
    xfactor_gui.show()
    return xfactor_gui


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QTimer
    import sys

    app = QApplication(sys.argv)
    print('before init')
    xfactor_gui = FactorAnalysisGUI()
    print('after init')

    def xfactor():
        xfactor_gui.show()

    QTimer.singleShot(1, xfactor)  # call startApp only after the GUI is ready
    sys.exit(app.exec_())

    sys.stdout = xlive_gui.emitstream_out
    sys.stderr = xlive_gui.emitstream_err

