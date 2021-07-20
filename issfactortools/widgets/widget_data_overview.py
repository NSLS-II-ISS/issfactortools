
import re
import sys
import numpy as np
import matplotlib.pyplot as plt
import pkg_resources
import traceback
import math

from PyQt5 import uic, QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QThread, QSettings
from PyQt5.QtWidgets import QMessageBox, QApplication, QWidget, QPushButton

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from issfactortools.elements.svd import plot_svd_results, doSVD

ui_path = pkg_resources.resource_filename('issfactortools', 'ui/ui_data_overview.ui')

class UIDataOverview(*uic.loadUiType(ui_path)):

    progress_sig = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.addCanvas()
        self.dataset = None

        self.pushButton_import_data.clicked.connect(self.import_data)

        self.pushButton_display_data.clicked.connect(self.display_data)


    def addCanvas(self):
        self.figure_data = Figure()
        #self.figure_data.set_facecolor(color='#E2E2E2')
        self.figure_data.ax = self.figure_data.add_subplot(111)
        self.canvas_data = FigureCanvas(self.figure_data)
        self.toolbar_data = NavigationToolbar(self.canvas_data, self)
        self.toolbar_data.resize(1, 10)
        self.layout_data_figure.addWidget(self.toolbar_data)
        self.layout_data_figure.addWidget(self.canvas_data)
        self.figure_data.tight_layout()
        self.canvas_data.draw()

        self.figure_svd= plt.figure()
        self.canvas = FigureCanvas(self.figure_svd)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.resize(1, 10)
        self.layout_svd_figure.addWidget(self.toolbar)
        self.layout_svd_figure.addWidget(self.canvas)
        self.figure_svd.tight_layout()
        self.canvas.draw()


    def import_data(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(directory='/nsls2/xf08id/Sandbox',
                                                         filter='*.xas', parent=self)[0]
        # if filename[-4:] == '.dat':
        #     filename = filename[:-4]

        self.dataset = np.genfromtxt(filename)



    def display_data(self):
        if self.dataset is not None:
            rows_text = self.rowsText.toPlainText()
            cols_text = self.columnsText.toPlainText()
            Myenergy = self.dataset[:, 0]
            self.figure_data.ax.clear()
            try:
                if rows_text == "" and cols_text == "":
                    self.figure_data.ax.plot(self.dataset[:, 0], self.dataset[:, 1:])
                    #Mydataset = self.dataset[:, 1:]
                elif rows_text == "" and cols_text != "":
                    cols = cols_text.split(",")
                    self.figure_data.ax.plot(self.dataset[:, 0], self.dataset[:, int(cols[0]):int(cols[1])])
                    #Mydataset = self.dataset[:, int(cols[0]):int(cols[1])]
                elif rows_text != "" and cols_text == "":
                    rows = rows_text.split(",")
                    self.figure_data.ax.plot(self.dataset[int(rows[0]):int(rows[1]), 0], self.dataset[int(rows[0]):int(rows[1]), 1:])
                    #Mydataset = self.dataset[int(rows[0]):int(rows[1]), 1:]
                else:
                    rows = rows_text.split(",")
                    cols = cols_text.split(",")
                    self.figure_data.ax.plot(self.dataset[int(rows[0]):int(rows[1]), 0], self.dataset[int(rows[0]):int(rows[1]), int(cols[0]):int(cols[1])])
                    #Mydataset = self.dataset[int(rows[0]):int(rows[1]), int(cols[0]):int(cols[1])]
            except Exception as err:
                QMessageBox.about(self, "INDEX ERROR", "The Rows and Columns Dimensions Are Invalid. Retry.")

            self.rowsText.clear()
            self.columnsText.clear()


            Mydataset = self.dataset[:, 1:]
            u, s, v, lra_chisq, ac_u, ac_v = doSVD(Mydataset)
            self.figure_svd.clear()
            plot_svd_results(u, s, v, lra_chisq, ac_u, ac_v, self.figure_svd, Myenergy, n_cmp_show=3)
            #plot_svd_results(u, s, v, lra_chisq, ac_u, ac_v, self.figure_svd, n_cmp_show=3)
            self.canvas.draw_idle()
            self.canvas_data.draw_idle()

