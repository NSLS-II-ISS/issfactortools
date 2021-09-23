
import re
import sys
import numpy as np
import matplotlib.pyplot as plt
import pkg_resources
import traceback
import math

import isstools.widgets
from PyQt5 import uic, QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QThread, QSettings, QPoint
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QMouseEvent
from PyQt5.QtWidgets import QMessageBox, QApplication, QWidget, QPushButton, QVBoxLayout, QMenu, QAction, QRadioButton, \
    QInputDialog, QFormLayout, QLineEdit, QTableWidgetItem, QTableWidget, QHeaderView

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
        self.file_formats = []
        self.tableWidget = None
        self.createTable()


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

    def import_data(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(directory='/nsls2/xf08id/Sandbox',
                                                         filter='*.xas', parent=self)[0]
        self.dataset = np.genfromtxt(filename)
        self.addNewFile(filename)

        Myenergy = self.dataset[:, 0]
        Mydataset = self.dataset[:, 1:]
        self.figure_solutions.ax.plot(Myenergy, Mydataset)
        self.canvas_solutions.draw_idle()

        numEnergy,ok = QInputDialog.getText(self,"Energy","Which columns contain energy?")
        numMu, ok = QInputDialog.getText(self, "Mu Normalized", "Which columns contain mu normalized")

        energyMu = numEnergy, numMu
        self.file_formats.append(energyMu)

        print(self.file_formats)
        print(ok)

