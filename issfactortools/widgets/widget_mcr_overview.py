
import re
import sys
import numpy as np
import matplotlib.pyplot as plt
import pkg_resources
import traceback
import math
import issfactortools.widgets.QDialog

import isstools.widgets
from PyQt5 import uic, QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QThread, QSettings, QPoint
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QMouseEvent
from PyQt5.QtWidgets import QMessageBox, QApplication, QWidget, QPushButton, QVBoxLayout, QMenu, QAction, QRadioButton, \
    QInputDialog, QFormLayout, QLineEdit, QTableWidgetItem, QTableWidget, QHeaderView, QDialogButtonBox

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
        self.createTable()

    def makeialog(self):
        self.first = QLineEdit(self)
        self.second = QLineEdit(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);

        layout = QFormLayout(self)
        layout.addRow("First text", self.first)
        layout.addRow("Second text", self.second)
        layout.addWidget(buttonBox)

        #buttonBox.accepted.connect(self.accept)
        #buttonBox.rejected.connect(self.reject)

    def getInputs(self):
        return (self.first.text(), self.second.text())

    def createTable(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        # Row count
        self.tableWidget.setRowCount(1)

        # Column count
        self.tableWidget.setColumnCount(3)

        self.tableWidget.setItem(0, 0, QTableWidgetItem("FILE NAME"))
        self.tableWidget.setItem(0, 1, QTableWidgetItem("LABEL"))
        self.tableWidget.setItem(0, 2, QTableWidgetItem("CHECKBOX"))

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
        numEnergy = int(energy.text())
        numMu = int(mu.text())
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
                Myenergy = self.file_formats[i - 2]["energy"]
                Mydataset = self.file_formats[i - 2]["mu"]
                self.figure_solutions.ax.plot(Myenergy, Mydataset)
                self.canvas_solutions.draw_idle()
            i = i + 1
        self.canvas_solutions.draw_idle()

    def import_data(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(directory='/nsls2/xf08id/Sandbox',
                                                         filter='*.xas', parent=self)[0]
        msgBox = issfactortools.widgets.QDialog.OpDialog()

        self.dataset = np.genfromtxt(filename)
        num_rows, num_cols = self.dataset.shape
        num = 0
        while num == 0:
            result = msgBox.exec_()
            print(msgBox.energy_line.text())
            print(msgBox.mu_line.text())
            num = self.dialogPrompts(msgBox.energy_line, msgBox.mu_line, num_cols, self.dataset)

        self.addNewFile(filename)






