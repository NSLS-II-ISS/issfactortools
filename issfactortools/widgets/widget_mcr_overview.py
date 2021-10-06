import inspect
import re
import sys
import numpy as np
import matplotlib.pyplot as plt
import pkg_resources
import traceback
import math
import issfactortools.widgets.QDialog
import pymcr.constraints
import isstools.widgets
from PyQt5 import uic, QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QThread, QSettings, QPoint
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QMouseEvent
from PyQt5.QtWidgets import QMessageBox, QApplication, QWidget, QPushButton, QVBoxLayout, QMenu, QAction, QRadioButton, \
    QInputDialog, QFormLayout, QLineEdit, QTableWidgetItem, QTableWidget, QHeaderView, QDialogButtonBox, QHBoxLayout, \
    QComboBox, QButtonGroup, QLabel

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from issfactortools.elements.svd import plot_svd_results, doSVD


ui_path = pkg_resources.resource_filename('issfactortools', 'ui/ui_mcr_overview.ui')

class UIDataOverview(*uic.loadUiType(ui_path)):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.addCanvas()
        self.pushButton_import_spectra.clicked.connect(self.import_data)
        self.pushButton_display_spectra.clicked.connect(self.display_data)
        self.file_formats = []
        self.tableWidget = None
        self.allConstraints = pymcr.constraints.__all__
        self.createTable()
        self.comboText = ""
        self.columnNames = ""
        self.num_cols = 0
        self.gridFilled = False
        self.x = { }
        for entry in self.allConstraints:
            self.x.update( {entry: 'inspect.signature(pymcr.constraints.'+entry+'.__init__)'})
        print(self.x)
        for key in self.x:
            print(eval(self.x[key]))
        print(self.x)
        self.createComboBox()



    def getColNammes(self):
        return self.columnNames

    def getNumCols(self):
        return self.num_cols


    def getInputs(self):
        return (self.first.text(), self.second.text())

    def createComboBox(self):
        self.combo = QComboBox()
        for key in self.x:
            self.combo.addItem(key)

        self.combo_layout.addWidget(self.combo)
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
            self.grid_layout.removeWidget(self.constraintT)
            row0.removeWidget(text)
            row1.removeWidget(radioS)
            row1.removeWidget(radioC)
            #self.grid_layout.removeWidget(row1)

        self.grid_layout.addLayout(row0)
        self.grid_layout.addLayout(row1)
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
        self.grid_layout.addWidget(self.constraintT)

        self.gridFilled = True

    def createTable(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        # Row count
        self.tableWidget.setRowCount(0)

        # Column count
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderItem(0, QTableWidgetItem("FILENAME"))
        self.tableWidget.setHorizontalHeaderItem(1, QTableWidgetItem("LABEL"))
        self.tableWidget.setHorizontalHeaderItem(2, QTableWidgetItem("CHECKBOX"))


        #self.tableWidget.setItem(0, 0, QTableWidgetItem("FILE NAME"))
        #self.tableWidget.setItem(0, 1, QTableWidgetItem("LABEL"))
        #self.tableWidget.setItem(0, 2, QTableWidgetItem("CHECKBOX"))

        # Table will fit the screen horizontally
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.table_layout.addWidget(self.tableWidget)


    def addCanvas(self):
        self.figure_curves = Figure()
        self.figure_curves.ax = self.figure_curves.add_subplot(111)
        self.canvas_curves = FigureCanvas(self.figure_curves)
        self.toolbar_curves = NavigationToolbar(self.canvas_curves, self)
        self.toolbar_curves.resize(1, 10)
        self.curves_layout.addWidget(self.toolbar_curves)
        self.curves_layout.addWidget(self.canvas_curves)
        self.figure_curves.tight_layout()
        self.canvas_curves.draw()
        #self.figure_curves.canvas.mpl_connect('button_press_event', self.onclick)

        self.figure_solutions = Figure()
        self.figure_solutions.ax = self.figure_solutions.add_subplot(111)
        self.canvas_solutions = FigureCanvas(self.figure_solutions)
        self.toolbar_solutions = NavigationToolbar(self.canvas_solutions, self)
        self.toolbar_solutions.resize(1, 10)
        self.solutions_layout.addWidget(self.toolbar_solutions)
        self.solutions_layout.addWidget(self.canvas_solutions)
        self.figure_solutions.tight_layout()
        self.canvas_solutions.draw()


    def addNewFile(self, filename):
        savedName = filename
        print(savedName)
        currentRows = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(currentRows + 1)
        self.tableWidget.setItem(currentRows, 0, QTableWidgetItem(savedName))
        chkBoxItem = QTableWidgetItem()
        chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        chkBoxItem.setCheckState(QtCore.Qt.Checked)
        print(chkBoxItem.checkState()) #0 is unchecked, 2 is checked, 1 is intermediate
        self.tableWidget.setItem(currentRows, 2, chkBoxItem)



    def dialogPrompts(self, mu, energy, cols, data):
        numEnergy = energy
        numMu = mu
        if (numEnergy >= cols or numMu >= cols or numEnergy < 0 or numMu < 0):
            QMessageBox.about(self, "ERROR", "INVALID COLUMN INDEX.")
            return 0
        else:
            x = data[:, numEnergy]
            y = data[:, numMu]
            dictionary = {'energy': x, 'mu': y}
            self.file_formats.append(dictionary)
            return 1


    def display_data(self):
        self.figure_solutions.ax.clear()
        numRows = self.tableWidget.rowCount()
        i = 0
        while i < numRows:
            item = self.tableWidget.item(i, 2).checkState()

            if (item == 2):
                Myenergy = self.file_formats[i - 1]["energy"]
                Mydataset = self.file_formats[i - 1]["mu"]
                self.figure_solutions.ax.plot(Myenergy, Mydataset)
                self.canvas_solutions.draw_idle()
            i = i + 1
        self.canvas_solutions.draw_idle()

    def saveSelections(self, t):

        currentRows = t.rowCount()
        currentColumns = t.columnCount()
        checkedOrNot = []
        for i in range(0, currentRows):
            arr = []
            for j in range(1, currentColumns):
                arr.append(t.item(i, j).checkState())
            checkedOrNot.append(arr)
        print(checkedOrNot)
        return checkedOrNot

    def import_data(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(directory='/nsls2/xf08id/Sandbox',
                                                         filter='*.xas', parent=self)[0]



        file = open(filename)
        content = file.readlines()
        self.columnNames = content[2]
        lastIndex = 0
        for i in range(0, len(self.columnNames)):
            if self.columnNames[i] == "#":
                lastIndex = i
        self.columnNames = self.columnNames[lastIndex+1:]
        self.columnNames = self.columnNames.split(",")
        #print(columnNames)
        file.close()
        self.dataset = np.genfromtxt(filename)
        num_rows, self.num_cols = self.dataset.shape

        num = 0

        print(self.columnNames)
        print(self.num_cols)

        msgBox = issfactortools.widgets.QDialog.OpDialog()


        test = QTableWidget()
        test.setRowCount(5)
        test.setColumnCount(5)
        row_4real = QHBoxLayout()
        row_4real.addWidget(test)
        msgBox.gui_init(self.num_cols, self.columnNames)

        while num == 0:
            result = msgBox.exec()
            tab = msgBox.row_4
            checks = self.saveSelections(tab)
            print("Here: "+str(tab))
            energy = []
            mu = []

            for i in range(0, tab.rowCount()):
                for j in range(0, tab.columnCount()-1):
                    print("X["+str(i)+"]["+str(j)+"]")
                    if checks[i][j] == 2:
                        if i == 0:
                            energy.append(j)
                        elif i == 1:
                            mu.append(j)

            print("E: "+str(energy))
            print("M: " +str(mu))



            num = self.dialogPrompts(energy[0], mu[0], self.num_cols, self.dataset)

        self.addNewFile(filename)


