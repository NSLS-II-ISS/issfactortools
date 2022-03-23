import copy
import re
import sys
import numpy as np
import pkg_resources
import inspect
import math
import os
import pymcr.constraints
from PyQt5 import uic, QtGui, QtCore, QtWidgets
from PyQt5.QtCore import QThread, QSettings, Qt
from PyQt5.QtGui import QStandardItem

from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QHeaderView, QRadioButton, QTableWidget, QHBoxLayout, \
    QLabel, QButtonGroup, QComboBox, QMenu, QAction, QMessageBox, QInputDialog
from PyQt5.QtCore import QTimer
import sys

import issfactortools
from issfactortools.widgets import widget_data_overview, widget_mcr_overview
from issfactortools.elements.mcrproject import DataSet, ReferenceSet, ConstraintSet, Optimizer, MCRProject
import issfactortools.widgets.QDialog

from issfactortools.dialogs.AddReferenceDialog import AddReferenceDialog


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
        self.pushButton_reference_from_file.clicked.connect(self.import_reference_from_file)
        self.plotMCRProject.clicked.connect(self.plotMCR)
        self.fitMCRProject.clicked.connect(self.fitMCR)
        self.model_datasets = QtGui.QStandardItemModel(self)  # model that is used to show listview of datasets
        self.model_references = QtGui.QStandardItemModel(self)  # model that is used to show listview of references
        self.model_constraints = QtGui.QStandardItemModel(self)  # model that is used to show listview of constraints
        self.model_mcrprojects = QtGui.QStandardItemModel(self)
        self.treeView_constraints.clicked.connect(self.updateComboBox)
        self.createMCRProject.clicked.connect(self.createMCR)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)

        self.allConstraints = pymcr.constraints.__all__
        # print(self.allConstraints)
        self.gridFilled = False
        self.x = {}
        self.y = {}
        for entry in self.allConstraints:
            if(entry == 'Constraint'):
                pass
            elif(entry == "ConstraintPlanarize"):
                cons = eval("pymcr.constraints." + entry + "([], [])")
                self.x.update({entry: cons})
                self.y.update({entry: 'inspect.signature(pymcr.constraints.' + entry + '.__init__)'})
            else:
                cons = eval("pymcr.constraints."+entry+"()")
                self.x.update({entry: cons})
                self.y.update({entry: 'inspect.signature(pymcr.constraints.' + entry + '.__init__)'})
            #self.x.update({entry: 'inspect.signature(pymcr.constraints.' + entry + '.__init__)'})
            #self.x.update({entry: 'cons = '+entry+'()'})


        self.createComboBox()

        self.comboText = ""
        self.columnNames = ""
        self.num_cols = 0

        self.dataOverview = issfactortools.widgets.widget_data_overview.UIDataOverview()

    #
    # self.widget_data_overview = widget_data_overview.UIDataOverview()
    # self.layout_data_overview.addWidget(self.widget_data_overview)
    #
    # self.widget_mcr_overview = widget_mcr_overview.UIDataOverview()
    # self.layout_mcr_analysis.addWidget(self.widget_mcr_overview)

    def updateComboBox(self):
        try:
            index = self.treeView_constraints.selectedIndexes()[0]
            crawler = index.model().itemFromIndex(index)
        except:
            pass
        try:
            constraint = crawler.text()
            constraint = constraint[0:len(constraint)-2]
            comboIndex = self.combo.findText(constraint)
            for i in range(0, self.combo.count()):
                if self.combo.itemText(i) == constraint:
                    comboIndex = i
                    break
            self.combo.setCurrentIndex(i)
        except:
            pass


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

    def _create_dataset(self, x, t_dict, data,
                        x_name='energy', t_name='index', data_name='mu norm',
                        x_units='eV', t_units='i', data_units='a.u.',
                        name='dataset'):
        item = self._make_item(name)
        item.item_type = 'DataSet'
        item.dataset = DataSet(x, t_dict, data,
                               x_name=x_name, t_name=t_name, data_name=data_name,
                               x_units=x_units, t_units=t_units, data_units=data_units,
                               name=name)
        self._append_item_to_model(self.model_datasets, item)
        self.listView_datasets.setModel(self.model_datasets)


    def unAppend_Constraint(self, item, index, cs):

        if(cs == "c"):

            del item.c_constraints[index]
        else:

            del item.st_constraints[index]


    def append_Constraint(self):
        index = self.treeView_constraints.selectedIndexes()[0]
        crawler = index.model().itemFromIndex(index)
        constr_params = None
        try:
            print(crawler.parent.text())
            QMessageBox.about(self, "ERROR", "Invalid Constraint Set Selected")
        except:
            if(self.c_clicked == False and self.s_clicked == False):
                QMessageBox.about(self, "ERROR", "No Vector Selected")
            else:
                selected = self.treeView_constraints.currentIndex().row()
                if selected == -1:
                    QMessageBox.about(self, "ERROR", "No Constraint Selected")
                else:
                    item = self.model_constraints.item(selected, 0)
                    txt = self.combo.currentText()
                    constr_params = self.x[txt]
                    # for i in range(0, self.constraintT.rowCount()):
                    #     for j in range(0, len(self.pArr[i])):
                    #         if j == 0:
                    #             if self.constraintT.item(i, j+1) is None:
                    #                 constr_params[str(self.constraintT.item(i, j).text())] = "None"
                    #             else:
                    #                 constr_params[str(self.constraintT.item(i, j).text())] = self.constraintT.item(i, j+1).text()

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
        radioC.setChecked(True)
        self.c_clicked = True
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
        parameters = str(eval(self.y[text]))
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
            menuAction3 = QAction("Duplicate", menu)
            menu.addAction(menuAction1)
            menu.addAction(menuAction2)
            menu.addAction(menuAction3)
            menuAction1.triggered.connect(self.renameConstraint)
            menuAction2.triggered.connect(self.deleteConstraint)
            menuAction3.triggered.connect(self.duplicateConstraint)
            menu.exec_(self.mapToGlobal(pos))

        elif(pos.x() >= 341 and pos.x() <= 637) and (pos.y() >= 32 and pos.y() <= 440):
            menu = QMenu(self)
            menuAction1 = QAction("Rename", menu)
            menuAction2 = QAction("Delete", menu)
            menuAction3 = QAction("Duplicate", menu)
            menu.addAction(menuAction1)
            menu.addAction(menuAction2)
            menu.addAction(menuAction3)
            menuAction1.triggered.connect(self.renameReference)
            menuAction2.triggered.connect(self.deleteReference)
            menuAction3.triggered.connect(self.duplicateReference)
            menu.exec_(self.mapToGlobal(pos))
        print("POS: ", pos.x(), pos.y())

    def duplicateReference(self):
        index = self.treeView_references.selectedIndexes()[0]
        item = self.model_references.item(index.row(), 0)
        itemcopy = self._make_item(item.text() + " Copy")
        itemcopy.item_type = 'ReferenceSet'
        itemcopy.reference = copy.deepcopy(item.reference)
        self._append_item_to_model(self.model_references, itemcopy)
        self.treeView_references.setModel(self.model_references)
        self.treeView_references.setHeaderHidden(True)
        for i in range(0, item.rowCount()):
            child = item.child(i, 0)
            childcopy = self._make_item(child.text(), False)
            self._append_child_to_item(childcopy, itemcopy)

    def deleteReference(self):
        index = self.treeView_references.selectedIndexes()[0]
        crawler = index.model().itemFromIndex(index)
        try:
            print(crawler.parent.text())
            parentAt = None
            arrIndex = -1
            for i in range(0, self.model_references.rowCount()):
                x = self.model_references.item(i, 0)
                if (x == crawler.parent):
                    parentAt = i
                    referenceItem = self.model_references.item(parentAt)
                    numChildren = referenceItem.rowCount()
                    item = self.model_references.item(parentAt, 0).takeRow(index.row())
                    self.removeFromReferenceSet(referenceItem.reference.reference_dict, crawler.text())
                    break
        except Exception as e:
            self.model_references.removeRow(index.row())

    def removeFromReferenceSet(self, dict, key):
        dict.pop(key)

    def duplicateConstraint(self):
        index = self.treeView_constraints.selectedIndexes()[0]
        item = self.model_constraints.item(index.row(), 0)
        itemcopy = self._make_item(item.text() + " Copy")
        itemcopy.item_type = 'ConstraintSet'
        itemcopy.constraint = copy.deepcopy(item.constraint)
        self._append_item_to_model(self.model_constraints, itemcopy)
        self.treeView_constraints.setModel(self.model_constraints)
        self.treeView_constraints.setHeaderHidden(True)
        for i in range(0, item.rowCount()):
            child = item.child(i, 0)
            childcopy = self._make_item(child.text(), False)
            self._append_child_to_item(childcopy, itemcopy)

    def deleteConstraint(self):
        index = self.treeView_constraints.selectedIndexes()[0]
        crawler = index.model().itemFromIndex(index)
        vector = crawler.text()[len(crawler.text())-1]
        vector = vector.lower()
        try:
            print(crawler.parent.text())
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



    def renameConstraint(self):
        text, ok = QInputDialog.getText(self, 'Rename Item', 'Enter the new name:')
        selected = self.treeView_constraints.currentIndex().row()

        item = self.model_constraints.item(selected, 0)
        item.setText(text)

    def renameReference(self):
        text, ok = QInputDialog.getText(self, 'Rename Item', 'Enter the new name:')
        selected = self.treeView_references.currentIndex().row()

        item = self.model_references.item(selected, 0)
        item.setText(text)

    def get_selected_reference_set_index(self):
        selection = self.treeView_references.selectedIndexes()
        if len(selection) == 0:
            QMessageBox.about(self, "ERROR", "No reference set selected")
            return
        elif len(selection) > 2:
            QMessageBox.about(self, "ERROR", "More than one reference set selected")
            return
        return self.treeView_references.selectedIndexes()[0]

    def add_references_to_set(self, x_list, data_list, label_list, index=None):
        if index is None:
            index = self.get_selected_reference_set_index()

        item = self.model_references.item(index.row(), 0)
        for x, data, label in zip(x_list, data_list, label_list):
            item.reference.append_reference(x, data, label)
            item_child = self._make_item(label, False)
            self._append_child_to_item(item_child, item)

    def add_references_to_specific_set(self, x_list, data_list, label_list, make_new_set=False):
        n_ref_sets = self.model_references.rowCount()
        if (n_ref_sets == 0):
            make_new_set = True

        if make_new_set:
            self._create_reference()
            last_index = self.model_references.rowCount() - 1
            index = self.model_references.item(last_index).index()
            self.add_references_to_set(x_list, data_list, label_list, index=index)
        else:
            refset_names = [self.model_references.item(i).text() for i in range(self.model_references.rowCount())]
            # print('BEFORE DIALOG')
            self.dialog = AddReferenceDialog(refset_names, parent=self)
            ret = self.dialog.exec_()
            # print(ret)
            if ret:
                idx = self.dialog.get_value()
                if idx == None:
                    self.add_references_to_specific_set(x_list, data_list, label_list, make_new_set=True)
                index = self.model_references.item(idx).index()
                self.add_references_to_set(x_list, data_list, label_list, index=index)




    def import_reference_from_file(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(directory='/nsls2/xf08id/Sandbox', filter='*.xas', parent=self)[0]
        filedata = np.genfromtxt(filename)
        x = filedata[:, 0]
        data = filedata[:, 1]
        label = os.path.split(filename)
        self.add_references_to_set([x], [data], [label])

    # def _add_references_from_db_proc(self, db_proc, uids):
    #     x_list = []
    #     data_list = []
    #     label_list = []
    #     for uid in uids:
    #         db_proc[uid]



    def import_dataset(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(directory='/nsls2/xf08id/Sandbox',
                                                         filter='*.xas', parent=self)[0]
        filedata = np.genfromtxt(filename)
        x = filedata[:, 0]
        data = filedata[:, 1:]
        t = np.arange(data.shape[1])
        self._create_dataset(x, t, data, name=filename)


    def inspectData(self):#, Dialog):
        rows = self.model_datasets.rowCount()
        cols = self.model_datasets.columnCount()
        # filename = ""
        selected = self.listView_datasets.currentIndex().row()
        item = self.model_datasets.item(selected, 0)
        dataset = item.dataset
        self.dataOverview.parse_data(dataset)
        self.dataOverview.show()

    def createMCR(self):
        Datasetrows = self.model_datasets.rowCount()
        Referencerows = self.model_references.rowCount()
        Constraintrows = self.model_constraints.rowCount()
        dataset = None
        referenceset = None
        constraintset = None
        for i in range(0, Datasetrows):
            if self.model_datasets.item(i,0).checkState() == 2:
                dataset = self.model_datasets.item(i, 0).dataset
                break
        for i in range(0, Referencerows):
            if self.model_references.item(i,0).checkState() == 2:
                referenceset = self.model_references.item(i,0).reference
                break
        for i in range(0, Constraintrows):
            if self.model_constraints.item(i,0).checkState() == 2:
                constraintset = self.model_constraints.item(i,0).constraint
                break

        if (dataset == None) or (referenceset == None) or (constraintset == None):
            QMessageBox.about(self, "ERROR", "Must select a data set, reference set, and constraint set")
        else:
            optimize = self._make_item("Optimizer")
            optimize.item_type = 'Optimizer'
            optimize.optimizer = Optimizer()

            project = self._make_item("MCR Project")
            project.item_type = "MCR Project"
            project.mcrproject = MCRProject(dataset, referenceset, constraintset, optimize.optimizer)
            self._append_item_to_model(self.model_mcrprojects, project)
            self.listView_datasets_2.setModel(self.model_mcrprojects)

    def fitMCR(self):
        index = self.listView_datasets_2.selectedIndexes()[0]
        item = self.model_mcrprojects.item(index.row(), 0)
        mcrProject = item.mcrproject
        mcrProject.fit()

    def plotMCR(self):
        index = self.listView_datasets_2.selectedIndexes()[0]
        item = self.model_mcrprojects.item(index.row(), 0)
        mcrProject = item.mcrproject
        mcrProject.plot_results()


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

