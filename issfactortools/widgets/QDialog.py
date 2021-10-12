from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QCheckBox
import re
import sys
import numpy as np
import matplotlib.pyplot as plt
import pkg_resources
import traceback
import math
import issfactortools.widgets.widget_mcr_overview
import issfactortools.widgets.widget_data_overview
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

import issfactortools


class OpDialog(QDialog):
    "A Dialog to set input and output ranges for an optimization."

    def __init__(self, *args, **kwargs):
        "Create a new dialogue instance."
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Column Selection")
        #mcr = issfactortools.widgets.widget_mcr_overview.UIDataOverview()
        #self.numC = mcr.getNumCols()
        #self.nameC = mcr.getColNammes()



    def gui_initDataOverview(self, filename):
        dataOverview = issfactortools.widgets.widget_data_overview.UIDataOverview()
        row_1 = QHBoxLayout()
        row_1.addWidget(dataOverview)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.buttonBox)
        layout = QVBoxLayout()
        #layout.addLayout(row_1)
        #layout.addLayout(row_2)
        layout.addLayout(row_1)
        dataOverview.import_data(filename)
        self.setLayout(layout)

    def gui_init(self, num_cols = 1, col_names = "XXX"):
        "Create and establish the widget layout."
        self.energy_line = QLineEdit()
        self.mu_line = QLineEdit()

        row_1 = QHBoxLayout()
        row_1.addWidget( QLabel("Energy"))
        row_1.addWidget(self.energy_line)

        row_2 = QHBoxLayout()
        row_2.addWidget(QLabel("Mu:"))
        row_2.addWidget(self.mu_line)




        row_4real = QHBoxLayout()

        self.row_4 = QTableWidget()
        self.row_4.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        # Row count
        self.row_4.setRowCount(len(col_names))
        self.row_4.setColumnCount((num_cols)+1)

        # Column count

        for i in range(0, len(col_names)):
            self.row_4.setItem(i, 0, QTableWidgetItem(col_names[i]))
            for j in range(1, num_cols+1):
                chkBoxItem = QTableWidgetItem()
                chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                chkBoxItem.setCheckState(QtCore.Qt.Unchecked)
                #chkBoxItem.stateChanged.connect(self.Test())
                self.row_4.setItem(i, j, chkBoxItem)


        for i in range(0,(num_cols)):
            self.row_4.setHorizontalHeaderItem(i+1, QTableWidgetItem("COL "+str(i)))


        #row_4.setItem(0, 0, QTableWidgetItem("FILE NAME"))
        #row_4.setItem(0, 1, QTableWidgetItem("LABEL"))
        #row_4.setItem(0, 2, QTableWidgetItem("CHECKBOX"))
        #row_4.setHorizontalHeaderItem(0, QTableWidgetItem("Whatever"))
        # Table will fit the screen horizontally
        self.row_4.horizontalHeader().setStretchLastSection(False)
        self.row_4.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        row_4real.addWidget(self.row_4)
        print(self.row_4)

        row_3 = QHBoxLayout()
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        row_3.addWidget(self.buttonBox)


        self.layout = QVBoxLayout()
        self.layout.addWidget(self.buttonBox)
        layout = QVBoxLayout()
        #layout.addLayout(row_1)
        #layout.addLayout(row_2)
        layout.addLayout(row_4real)
        layout.addLayout(row_3)
        self.setLayout(layout)
        print(str(self.energy_line))
        print(str(self.mu_line))
