import re
import sys
import numpy as np
import pkg_resources
import inspect
import math
import pymcr.constraints
from PyQt5 import uic, QtGui, QtCore, QtWidgets
from PyQt5.QtCore import QThread, QSettings, Qt

import issfactortools
from issfactortools.widgets import widget_data_overview, widget_mcr_overview
from issfactortools.elements.mcrproject import DataSet, ReferenceSet, ConstraintSet
import issfactortools.widgets.QDialog
ui_path = pkg_resources.resource_filename('issfactortools', 'ui/ui_main.ui')



class FactorAnalysisGUI(*uic.loadUiType(ui_path)):

    progress_sig = QtCore.pyqtSignal()

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.parent = parent

        self.pushButton_2.clicked.connect(self.import_dataset)
        self.model_datasets = QtGui.QStandardItemModel(self) # model that is used to show listview of datasets
        self.model_references = QtGui.QStandardItemModel(self)  # model that is used to show listview of references
        self.model_constraints = QtGui.QStandardItemModel(self)  # model that is used to show listview of constraints

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)

        self.allConstraints = pymcr.constraints.__all__
        self.gridFilled = False
        self.x = {}
        for entry in self.allConstraints:
            self.x.update({entry: 'inspect.signature(pymcr.constraints.' + entry + '.__init__)'})
        self.createComboBox()

        self.comboText = ""
        self.columnNames = ""
        self.num_cols = 0

        print(self.x)
        for key in self.x:
            print(eval(self.x[key]))
        print(self.x)
        self.dataOverview = issfactortools.widgets.widget_data_overview.UIDataOverview

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

    def createComboBox(self):
        self.combo = QComboBox()
        for key in self.x:
            self.combo.addItem(key)

        self.verticalLayout.addWidget(self.combo)
        self.combo.currentIndexChanged.connect(self.constraintTable)

    def constraintTable(self):
        radioC = QRadioButton()
        radioS = QRadioButton()
        radioS.setText("S")
        radioC.setText("C")
        radioS.setChecked(False)
        radioC.setChecked(False)
        CSGroup = QButtonGroup()
        CSGroup.addButton(radioS)
        CSGroup.addButton(radioC)
        #self.grid_layout.addWidget(radioS)
        #self.grid_layout.addWidget(radioC)

        text = QLabel()
        text.setText("Which vector should the constraint be applied to?")
        row0 = QHBoxLayout()
        row0.addWidget(text)
        row1 = QHBoxLayout()
        row1.addWidget(radioC)
        row1.addWidget(radioS)

        if self.gridFilled == True:
            self.verticalLayout.removeWidget(self.constraintT)
            row0.removeWidget(text)
            row1.removeWidget(radioS)
            row1.removeWidget(radioC)
            #self.grid_layout.removeWidget(row1)

        self.verticalLayout.addLayout(row0)
        self.verticalLayout.addLayout(row1)
        self.constraintT = QTableWidget()
        text = self.combo.currentText()
        parameters = str(eval(self.x[text]))
        print(parameters)
        parametersList = list(parameters)
        for char in parametersList: #remove any punctuation to make it neater in the grid
            if char == ")" or char == "(":
                del parametersList[parametersList.index(char)]

        parameters = "".join(parametersList)
        print(parameters)

        radio = QRadioButton()



        pArr = parameters.split(",")
        if "self" in pArr[0]:
            del pArr[0]
        print(pArr)
        self.constraintT.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.constraintT.setRowCount(len(pArr))
        self.constraintT.setColumnCount(2)

        self.constraintT.setHorizontalHeaderItem(0, QTableWidgetItem("PARAMETER"))
        self.constraintT.setHorizontalHeaderItem(1, QTableWidgetItem("VALUE"))
        #self.constraintT.setHorizontalHeaderItem(2, QTableWidgetItem("C"))
        #self.constraintT.setHorizontalHeaderItem(3, QTableWidgetItem("S"))
        for i in range(0, len(pArr)):
            pArr[i] = pArr[i].split("=")

        for i in range(0, self.constraintT.rowCount()):
            for j in range(0, len(pArr[i])):
                self.constraintT.setItem(i, j, QTableWidgetItem(str(pArr[i][j])))

        #for i in range(0, self.constraintT.rowCount()):
         #   bGroup = QButtonGroup()
          #  for j in range(2, 4):
           #     rad = QRadioButton()
            #    self.constraintT.setCellWidget(i, j, rad)
             #   bGroup.addButton(rad)

        #self.constraintT.setCellWidget(0, 2, radio)

        self.constraintT.horizontalHeader().setStretchLastSection(False)
        self.constraintT.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.verticalLayout.addWidget(self.constraintT)

        self.gridFilled = True



    def showMenu(self, pos):
        if (pos.x() >= 12 and pos.x() <= 310) and (pos.y() >= 32 and pos.y() <= 440):
            menu = QMenu(self)

            menuAction1 = QAction("Inspect", menu)
            menu.addAction(menuAction1)
            print(self.model_datasets.rowCount())
            print(self.model_datasets.columnCount())
            print(self.model_datasets.item(0, 0).checkState())

            menuAction1.triggered.connect(self.inspectData)
            #menuAction1.triggered.connect(self.verticalLines)
            #menuAction2.triggered.connect(self.clearplot2)
            #menuAction3.triggered.connect(self.normalizedLines)


            menu.exec_(self.mapToGlobal(pos))
        print("POS: ",pos.x(), pos.y())
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


        #self.dataOverview.show()
        filename = QtWidgets.QFileDialog.getOpenFileName(directory='/nsls2/xf08id/Sandbox',
                                                         filter='*.xas', parent=self)[0]
        filedata = np.genfromtxt(filename)
        x = filedata[:, 0]
        data = filedata[:, 1:]
        t = np.arange(data.shape[1])
        self._create_dataset(x, t, data, name=filename)




    def inspectData(self, Dialog):
        rows = self.model_datasets.rowCount()
        cols = self.model_datasets.columnCount()
        filename = ""
        for i in range(0, rows):
            for j in range(0, cols):
                item = self.model_datasets.item(i, j)
                checkState = item.checkState()
                if(checkState == 2):
                    filename = item.text()
        msgBox = issfactortools.widgets.QDialog.OpDialog()
        msgBox.gui_initDataOverview(filename)
        result = msgBox.exec()




def main_show():
    xfactor_gui = FactorAnalysisGUI()
    xfactor_gui.show()
    return xfactor_gui


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QHeaderView, QRadioButton, QTableWidget, QHBoxLayout, \
    QLabel, QButtonGroup, QComboBox, QMenu, QAction
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

