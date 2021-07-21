
import re
import sys
import numpy as np
import matplotlib.pyplot as plt
import pkg_resources
import traceback
import math

import isstools.widgets
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
        self.figure_data.ax = self.figure_data.add_subplot(211)
        self.figure_data.ax2 = self.figure_data.add_subplot(212)
        self.canvas_data = FigureCanvas(self.figure_data)
        self.toolbar_data = NavigationToolbar(self.canvas_data, self)
        self.toolbar_data.resize(1, 10)
        self.layout_data_figure.addWidget(self.toolbar_data)
        self.layout_data_figure.addWidget(self.canvas_data)
        self.figure_data.tight_layout()
        self.canvas_data.draw()

        self.figure_svd= plt.figure()
        self.figure_svd.ax = self.figure_svd.add_subplot(221)
        self.figure_svd.ax2 = self.figure_svd.add_subplot(222)
        self.figure_svd.ax3 = self.figure_svd.add_subplot(223)
        self.figure_svd.ax4 = self.figure_svd.add_subplot(224)
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
        Myenergy = self.dataset[:, 0]
        #print(Myenergy)



    def getFirstLimit(self, num, arr):
        i = 0
        fR = 0
        while i < len(arr):
            if arr[i] >= num:
                fR= i
                return i, fR
            i = i + 1

    def getSecondLimit(self, num, arr, index):
        sR = 0
        i = index
        while i < len(arr):
            if arr[i] >= num:
                sR = i
                return sR
            i = i + 1

    def display_data(self):
        components = 3
        if self.dataset is not None:
            rows_text = self.rowsText.toPlainText()
            cols_text = self.columnsText.toPlainText()
            components_text = self.componentsText.toPlainText()
            components_text2 = self.componentsText2.toPlainText()
            energy_text = self.energyText.toPlainText()
            if components_text == "" and components_text2 == "":
                components = 3
            elif components_text != "" and components_text2 == "":
                if int(components_text) <= 0:
                    QMessageBox.about(self, "ERROR", "The number of components is too low. Retry.")
                else:
                    components = int(components_text)
            elif components_text == "" and components_text2 != "":
                if int(components_text2) <= 0:
                    QMessageBox.about(self, "ERROR", "The number of components is too low. Retry.")
                else:
                    components = int(components_text2)




            self.figure_data.ax.clear()

            Myenergy = self.dataset[:, 0]
            Mydataset = self.dataset[:, 1:]

            if energy_text == "":
                Myenergy = self.dataset[:, 0]
                Mydataset = self.dataset[:, 1:]
            elif energy_text != "":
                energy_text = energy_text.split(",")
                if int(energy_text[0]) < Myenergy[0] or int(energy_text[1]) > Myenergy[len(Myenergy)-1]:
                    QMessageBox.about(self, "ERROR", "The energy range is invalid. Displaying default range.")
                else:
                    i, firstRow = self.getFirstLimit(int(energy_text[0]), Myenergy)
                    secondRow = self.getSecondLimit(int(energy_text[1]), Myenergy, i)
                    print("First Row: " + str(firstRow))
                    print("Second Row: " + str(secondRow))
                    Mydataset = self.dataset[firstRow:secondRow, 1:]
                    Myenergy = self.dataset[firstRow:secondRow, 0]
                    Myenergy = np.array(Myenergy)
                    print(self.dataset[:,0])
                    print(Mydataset[1:3, 1:3])

            try:
                if rows_text == "" and cols_text == "":
                    self.figure_data.ax.plot(Myenergy, Mydataset)
                elif rows_text == "" and cols_text != "":
                    cols = cols_text.split(",")
                    if energy_text == "":
                        self.figure_data.ax.plot(self.dataset[:, 0], self.dataset[:, int(cols[0]):int(cols[1])])
                    else:
                        self.figure_data.ax.plot(Myenergy[:, 0], Mydataset[:, int(cols[0]):int(cols[1])])
                elif rows_text != "" and cols_text == "":
                    rows = rows_text.split(",")
                    if energy_text == "":
                        self.figure_data.ax.plot(self.dataset[int(rows[0]):int(rows[1]), 0], self.dataset[int(rows[0]):int(rows[1]), 1:])
                    else:
                        self.figure_data.ax.plot(Myenergy[int(rows[0]):int(rows[1]), 0],   Mydataset[int(rows[0]):int(rows[1]), 1:])
                else:
                    rows = rows_text.split(",")
                    cols = cols_text.split(",")
                    if energy_text == "":
                        self.figure_data.ax.plot(self.dataset[int(rows[0]):int(rows[1]), 0], self.dataset[int(rows[0]):int(rows[1]), int(cols[0]):int(cols[1])])
                    else:
                        self.figure_data.ax.plot(Myenergy[int(rows[0]):int(rows[1]), 0],  Mydataset[int(rows[0]):int(rows[1]), int(cols[0]):int(cols[1])])
            except Exception as err:
                print(err)
                QMessageBox.about(self, "INDEX ERROR", "The Rows and Columns Dimensions Are Invalid. Retry.")





            self.rowsText.clear()
            self.columnsText.clear()
            self.componentsText.clear()
            self.componentsText2.clear()
            self.energyText.clear()




            u, s, v, lra_chisq, ac_u, ac_v = doSVD(Mydataset)
            self.figure_svd.clear()
            plot_svd_results(u, s, v, lra_chisq, ac_u, ac_v, self.figure_svd, Myenergy, n_cmp_show=components)
            self.canvas.draw_idle()
            self.canvas_data.draw_idle()

