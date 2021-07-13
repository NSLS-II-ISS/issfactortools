
import re
import sys
import numpy as np
import matplotlib.pyplot as plt
import pkg_resources
import math

from PyQt5 import uic, QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QThread, QSettings

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

ui_path = pkg_resources.resource_filename('issfactortools', 'ui/ui_data_overview.ui')

class UIDataOverview(*uic.loadUiType(ui_path)):

    progress_sig = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.addCanvas()

        self.pushButton_import_data.clicked.connect(self.import_data)



    def addCanvas(self):
        self.figure_data = Figure()
        #self.figure_data.set_facecolor(color='#E2E2E2')
        self.figure_data.ax = self.figure_data.add_subplot(111)
        self.canvas = FigureCanvas(self.figure_data)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.resize(1, 10)
        self.layout_data_figure.addWidget(self.toolbar)
        self.layout_data_figure.addWidget(self.canvas)
        self.figure_data.tight_layout()
        self.canvas.draw()



    def import_data(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(directory='/nsls2/xf08id/Sandbox',
                                                         filter='*.dat', parent=self)[0]
        # if filename[-4:] == '.dat':
        #     filename = filename[:-4]

        self.dataset = np.genfromtxt(filename)

        self.figure_data.ax.plot(self.dataset[:, 0], self.dataset[:, 1])
        self.canvas.draw_idle()
        # plt.figure()
        # plt.plot(self.dataset[:, 0], self.dataset[:, 1])
        # plt.show()
        # plt.ion()
