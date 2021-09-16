
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
from PyQt5.QtWidgets import QMessageBox, QApplication, QWidget, QPushButton, QVBoxLayout, QMenu, QAction, QRadioButton

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

    def addCanvas(self):
        self.figure_curves = Figure()
        self.canvas_curves = FigureCanvas(self.figure_curves)
        self.toolbar_curves = NavigationToolbar(self.canvas_curves, self)
        self.toolbar_curves.resize(1, 10)
        self.curves_layout.addWidget(self.toolbar_curves)
        self.curves_layout.addWidget(self.canvas_curves)
        self.figure_curves.tight_layout()
        self.canvas_curves.draw()
        #self.figure_curves.canvas.mpl_connect('button_press_event', self.onclick)

        self.figure_solutions = Figure()
        self.canvas_solutions = FigureCanvas(self.figure_solutions)
        self.toolbar_solutions = NavigationToolbar(self.canvas_solutions, self)
        self.toolbar_solutions.resize(1, 10)
        self.solutions_layout.addWidget(self.toolbar_solutions)
        self.solutions_layout.addWidget(self.canvas_solutions)
        self.figure_solutions.tight_layout()
        self.canvas_solutions.draw()
