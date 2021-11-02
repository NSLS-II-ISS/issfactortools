import re
import sys
import numpy as np
import pkg_resources
import inspect
import math
import pymcr.constraints
from PyQt5 import uic, QtGui, QtCore, QtWidgets
from PyQt5.QtCore import QThread, QSettings, Qt

from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QHeaderView, QRadioButton, QTableWidget, QHBoxLayout, \
    QLabel, QButtonGroup, QComboBox, QMenu, QAction, QMessageBox, QInputDialog
from PyQt5.QtCore import QTimer
import sys

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

        self.c_clicked = False
        self.s_clicked = False
        self.pushButton_2.clicked.connect(self.import_dataset)
        self.pushButton_create_constraint_set.clicked.connect(self._create_constraint)
        self.appendConstraint.clicked.connect(self.append_Constraint)
        self.createReference.clicked.connect(self._create_reference)
        self.model_datasets = QtGui.QStandardItemModel(self)  # model that is used to show listview of datasets
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
        self.dataOverview = issfactortools.widgets.widget_data_overview.UIDataOverview()

    #
    # self.widget_data_overview = widget_data_overview.UIDataOverview()
    # self.layout_data_overview.addWidget(self.widget_data_overview)
    #
    # self.widget_mcr_overview = widget_mcr_overview.UIDataOverview()
    # self.layout_mcr_analysis.addWidget(self.widget_mcr_overview)


    def _append_item_to_model(self, model, item):
        parent = model.invisibleRootItem()
        parent.appendRow(item)
        item.parent = model

    def _append_child_to_item(self, child, item):
        item.appendRow(child)
        child.parent = item



    def _make_item(self, name, checkable = True, dropdown = False):
        item = QtGui.QStandardItem(name)
        item.setDropEnabled(False)
        if checkable:
            item.setCheckable(True)
        else:
            item.setCheckable(False)
        item.setEditable(False)
        return item

    def _create_constraint(self, name='New Constraint'):
        name = "New Constraint"
        #print(name)
        item = self._make_item(name)
        item.item_type = 'ConstraintSet'
        item.constraint = ConstraintSet()
        self._append_item_to_model(self.model_constraints, item)
        self.treeView_constraints.setModel(self.model_constraints)
        self.treeView_constraints.setHeaderHidden(True)


    def _create_reference(self, dict={}, name='New Reference'):
        item = self._make_item(name)
        item.item_type = 'ReferenceSet'
        item.reference = ReferenceSet()
        self._append_item_to_model(self.model_references, item)
        self.treeView_references.setModel(self.model_references)
        self.treeView_references.setHeaderHidden(True)

    def _create_dataset(self, x, t, data, name='DataSet'):
        item = self._make_item(name)
        item.item_type = 'DataSet'
        item.dataset = DataSet(x, t, data, name)
        self._append_item_to_model(self.model_datasets, item)
        self.listView_datasets.setModel(self.model_datasets)

    def unAppend_Constraint(self, item, index, cs):
        print("Do I run?")
        if(cs == "c"):
            print("Here!")
            del item.c_constraints[index]
        else:
            print("No! I'm here!")
            del item.st_constraints[index]
    def append_Constraint(self):
        constr_params = {}
        if(self.c_clicked == False and self.s_clicked == False):
            QMessageBox.about(self, "ERROR", "No Vector Selected")
        else:
            selected = self.treeView_constraints.currentIndex().row()
            if selected == -1:
                QMessageBox.about(self, "ERROR", "No Constraint Selected")
            else:
                item = self.model_constraints.item(selected, 0)
                for i in range(0, self.constraintT.rowCount()):
                    for j in range(0, len(self.pArr[i])):
                        if j == 0:
                            if self.constraintT.item(i, j+1) is None:
                                constr_params[str(self.constraintT.item(i, j).text())] = "None"
                            else:
                                constr_params[str(self.constraintT.item(i, j).text())] = self.constraintT.item(i, j+1).text()

                        #constr =  self.constraintT.item(i, j).text()
                        #constr_params += str(constr)
                if self.c_clicked:
                    item.constraint.append_c_constraint(constr_params)
                    vector = " C"
                elif self.s_clicked:
                    item.constraint.append_st_constraint(constr_params)
                    vector = " S"

                constraint_item = self._make_item(self.combo.currentText() + vector, False) #go through combobox

                self._append_child_to_item(constraint_item, item)
                print(item.constraint.c_constraints)
                print(item.constraint.st_constraints)

    def createComboBox(self):
        self.combo = QComboBox()
        for key in self.x:
            self.combo.addItem(key)

        self.verticalLayout.addWidget(self.combo)
        self.combo.currentIndexChanged.connect(self.constraintTable)

    def SEnabled(self):
        self.s_clicked = True
        self.c_clicked = False
    def CEnabled(self):
        self.s_clicked = False
        self.c_clicked = True

    def constraintTable(self):
        radioC = QRadioButton()
        radioS = QRadioButton()
        radioS.setText("S")
        radioC.setText("C")
        radioS.setChecked(False)
        radioC.setChecked(False)
        radioS.clicked.connect(self.SEnabled)
        radioC.clicked.connect(self.CEnabled)
        self.CSGroup = QButtonGroup()
        self.CSGroup.addButton(radioS)
        self.CSGroup.addButton(radioC)
        # self.grid_layout.addWidget(radioS)
        # self.grid_layout.addWidget(radioC)

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
            # self.grid_layout.removeWidget(row1)

        self.verticalLayout.addLayout(row0)
        self.verticalLayout.addLayout(row1)
        self.constraintT = QTableWidget()
        text = self.combo.currentText()
        parameters = str(eval(self.x[text]))
        print(parameters)
        parametersList = list(parameters)
        for char in parametersList:  # remove any punctuation to make it neater in the grid
            if char == ")" or char == "(":
                del parametersList[parametersList.index(char)]

        parameters = "".join(parametersList)
        print(parameters)

        radio = QRadioButton()

        self.pArr = parameters.split(",")
        if "self" in self.pArr[0]:
            del self.pArr[0]
        print(self.pArr)
        self.constraintT.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.constraintT.setRowCount(len(self.pArr))
        self.constraintT.setColumnCount(2)

        self.constraintT.setHorizontalHeaderItem(0, QTableWidgetItem("PARAMETER"))
        self.constraintT.setHorizontalHeaderItem(1, QTableWidgetItem("VALUE"))
        # self.constraintT.setHorizontalHeaderItem(2, QTableWidgetItem("C"))
        # self.constraintT.setHorizontalHeaderItem(3, QTableWidgetItem("S"))
        for i in range(0, len(self.pArr)):
            self.pArr[i] = self.pArr[i].split("=")

        for i in range(0, self.constraintT.rowCount()):
            for j in range(0, len(self.pArr[i])):
                self.constraintT.setItem(i, j, QTableWidgetItem(str(self.pArr[i][j])))   #use this for getting the proper constraints

        # for i in range(0, self.constraintT.rowCount()):
        #   bGroup = QButtonGroup()
        #  for j in range(2, 4):
        #     rad = QRadioButton()
        #    self.constraintT.setCellWidget(i, j, rad)
        #   bGroup.addButton(rad)

        # self.constraintT.setCellWidget(0, 2, radio)

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
            # menuAction1.triggered.connect(self.verticalLines)
            # menuAction2.triggered.connect(self.clearplot2)
            # menuAction3.triggered.connect(self.normalizedLines)

            menu.exec_(self.mapToGlobal(pos))
        elif(pos.x() >= 683 and pos.x() <= 980) and (pos.y() >= 32 and pos.y()<=440):
            menu = QMenu(self)
            menuAction1 = QAction("Rename", menu)
            menuAction2 = QAction("Delete", menu)
            menu.addAction(menuAction1)
            menu.addAction(menuAction2)
            menuAction1.triggered.connect(self.renameItem)
            menuAction2.triggered.connect(self.deleteConstraint)
            menu.exec_(self.mapToGlobal(pos))
            print("Hello")
        print("POS: ", pos.x(), pos.y())


    def deleteConstraint(self):
        index = self.treeView_constraints.selectedIndexes()[0]
        crawler = index.model().itemFromIndex(index)
        vector = crawler.text()[len(crawler.text())-1]
        vector = vector.lower()
        try:
            parentAt = None
            arrIndex = -1
            for i in range(0, self.model_constraints.rowCount()):
                x = self.model_constraints.item(i, 0)
                if (x == crawler.parent):
                    parentAt = i
                    constraintItem = self.model_constraints.item(parentAt)
                    numChildren = constraintItem.rowCount()
                    for j in range(0, numChildren):
                        child = constraintItem.child(j, 0)
                        if(child.text()[len(child.text())-1].lower() == vector):
                            arrIndex = arrIndex+1
                            if(child == crawler):
                                break


                    item = self.model_constraints.item(parentAt, 0).takeRow(index.row())
                    self.unAppend_Constraint(constraintItem.constraint, arrIndex, vector)
                    break
        except:
              self.model_constraints.removeRow(index.row())



    def renameItem(self): #currently will only work for constraints, later will work for database and references as well
        text, ok = QInputDialog.getText(self, 'Rename Item', 'Enter the new name:')
        selected = self.treeView_constraints.currentIndex().row()
        print(selected)
        item = self.model_constraints.item(selected, 0)
        item.setText(text)


    def import_dataset(self):
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
        selected = self.listView_datasets.currentIndex().row()
        item = self.model_datasets.item(selected, 0)
        dataset = item.dataset
        self.dataOverview.parse_data(dataset)
        self.dataOverview.show()


def main_show():
    xfactor_gui = FactorAnalysisGUI()
    xfactor_gui.show()
    return xfactor_gui


if __name__ == '__main__':


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

