from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel
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
    QInputDialog, QFormLayout, QLineEdit, QTableWidgetItem, QTableWidget, QHeaderView, QDialogButtonBox

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure



class OpDialog(QDialog):
    "A Dialog to set input and output ranges for an optimization."

    def __init__(self, *args, **kwargs):
        "Create a new dialogue instance."
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Column Selection")
        self.gui_init()

    def gui_init(self):
        "Create and establish the widget layout."
        self.energy_line = QLineEdit()
        self.mu_line = QLineEdit()

        row_1 = QHBoxLayout()
        row_1.addWidget( QLabel("Energy"))
        row_1.addWidget(self.energy_line)

        row_2 = QHBoxLayout()
        row_2.addWidget(QLabel("Mu:"))
        row_2.addWidget(self.mu_line)

        row_3 = QHBoxLayout()
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        row_3.addWidget(self.buttonBox)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.buttonBox)
        layout = QVBoxLayout()
        layout.addLayout(row_1)
        layout.addLayout(row_2)
        layout.addLayout(row_3)
        self.setLayout(layout)
        print(str(self.energy_line))
        print(str(self.mu_line))