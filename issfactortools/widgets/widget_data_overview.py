import copy
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
from PyQt5.QtWidgets import QMessageBox, QApplication, QWidget, QPushButton, QVBoxLayout, QMenu, QAction, QRadioButton, QListWidgetItem

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

        self.data_graph = None

        self.dataset = None
        self.mouseCoords = 0,0

        self.addCanvas()

        self.clearButton.clicked.connect(self.clearText)
        self.pushButton_display_data.clicked.connect(self.display_data)

        self.offset_text = self.dataOffset.toPlainText()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)


    def clearText(self):
        self.columnsText.clear()
        self.componentsText.clear()
        self.energyText.clear()
        self.svd_auto_limits.clear()
        self.dataOffset.clear()
        self.svd_sing_limits.clear()
        self.dataOffsetWhole.clear()

    def verticalLines(self):
        self.offset_text = self.dataOffset.toPlainText()
        if self.dataset is not None:
            ymin, ymax = self.figure_data.ax.get_ylim()
            col = ''
            print(ymax)
            energy = self.dataset._x
            if(self.mouseCoords[0] <= energy.max() and self.mouseCoords[0] >= energy.min()):
                num = self.findclosest(self.dataset._x, self.mouseCoords[0])
                i= np.where(self.dataset._x == num)
                #print("Index: ", i[0])
                shape = self.dataset._data[i[0], :].shape
                arr1d = self.dataset._data[i[0], 1:].flatten()
                #print(arr1d)
                if self.offset_text == "":
                    col = self.figure_data.ax2.plot(arr1d, ".-")
                    self.figure_data.ax2.set_xlabel("Spectrum Number")
                    self.figure_data.ax2.set_ylabel('Mu Normalized')
                else:
                    col = self.figure_data.ax2.plot(arr1d + float(self.offset_text), ".-")
                    self.figure_data.ax2.set_xlabel("Spectrum Number")
                    self.figure_data.ax2.set_ylabel('Mu Normalized')
                print(col[0].get_color())
                #self.figure_data.ax2.yaxis.tick_right()

            #self.figure_data.ax.vlines(self.mouseCoords[0], self.mouseCoords[1], self.mouseCoords[1] + 0.1, color= col[0].get_color())
            #self.figure_data.ax.vlines(self.mouseCoords[0], 0, ymax - (ymax*0.005), color=col[0].get_color())
            self.figure_data.ax.vlines(self.mouseCoords[0], 0, ymax, color=col[0].get_color())
            print(ymax)

            self.canvas_data.draw()
        else:
            QMessageBox.about(self, "ERROR", "You must import a dataset first.")

    def normalizedLines(self):
        if self.dataset is not None:
            ymin, ymax = self.figure_data.ax.get_ylim()
            col = ''
            print(ymax)
            energy = self.dataset._x
            if(self.mouseCoords[0] <= energy[energy.size-1] and self.mouseCoords[0] >= energy[0]):
                print("Here!")
                num = self.findclosest(self.dataset._x, self.mouseCoords[0])
                i= np.where(self.dataset._x == num)
                print("Index: ", i[0])
                shape = self.dataset._data[i[0], :].shape
                arr1d = self.dataset._data[i[0], 1:].flatten()
                max = np.max(arr1d)
                min = np.min(arr1d)
                print(max)
                print(min)
                newArr = []
                for val in arr1d:
                    val = ((val - min)/(max-min))
                    print(val)
                    newArr.append(val)
                print(arr1d)
                col = self.figure_data.ax2.plot(newArr, ".-")
                self.figure_data.ax.vlines(self.mouseCoords[0], 0, ymax - (ymax*0.005), col[0].get_color())
            self.canvas_data.draw_idle()
        else:
            QMessageBox.about(self, "ERROR", "You must import a dataset first.")

    def onclick(self, event):
        print('you pressed', event.button, event.xdata, event.ydata)
        self.mouseCoords = event.xdata, event.ydata

    def clearplot2(self):
        if self.dataset is not None:
            self.figure_data.ax2.clear()
            self.figure_data.ax.clear()
            self.canvas_data.draw()
            self.display_data()
        self.canvas.draw_idle()
        self.canvas_data.draw_idle()

    def showMenu(self, pos):
        if (pos.x() >= 390 and pos.x() <= 850) and (pos.y() >= 90 and pos.y() <= 435):
            menu = QMenu(self)

            menuAction1 = QAction("Add line", menu)
            menu.addAction(menuAction1)

            menuAction2 = QAction("Remove all lines", menu)
            menu.addAction(menuAction2)

            menuAction3 = QAction("Add line(normalized)", menu)
            menu.addAction(menuAction3)

            menu_sort_by_int = QAction("Sort by signal at this energy", menu)
            menu.addAction(menu_sort_by_int)

            menuAction1.triggered.connect(self.verticalLines)
            menuAction2.triggered.connect(self.clearplot2)
            menuAction3.triggered.connect(self.normalizedLines)
            menu_sort_by_int.triggered.connect(self.sort_data_by)

            menu.exec_(self.mapToGlobal(pos))
        print("POS: ",pos.x(), pos.y())

    def addCanvas(self):
        self.figure_data = Figure()
        self.figure_data.ax = self.figure_data.add_subplot(211)
        self.data_graph = self.figure_data.ax
        self.figure_data.ax2 = self.figure_data.add_subplot(212)
        self.canvas_data = FigureCanvas(self.figure_data)
        self.toolbar_data = NavigationToolbar(self.canvas_data, self)
        self.toolbar_data.resize(1, 10)
        self.layout_data_figure.addWidget(self.toolbar_data)
        self.layout_data_figure.addWidget(self.canvas_data)
        self.figure_data.tight_layout()
        self.canvas_data.draw()
        self.figure_data.canvas.mpl_connect('button_press_event', self.onclick)

        # self.figure_svd= plt.figure()
        self.figure_svd = Figure()
        self.figure_svd.ax = self.figure_svd.add_subplot(211)
        self.figure_svd.ax2 = self.figure_svd.add_subplot(212)

        self.canvas = FigureCanvas(self.figure_svd)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.resize(1, 10)
        self.layout_svd_figure.addWidget(self.toolbar)
        self.layout_svd_figure.addWidget(self.canvas)
        self.figure_svd.tight_layout()
        self.canvas.draw()

        # self.figure_stat = plt.figure()
        self.figure_stat = Figure()
        self.figure_stat.ax3 = self.figure_stat.add_subplot(211)
        self.figure_stat.ax4 = self.figure_stat.add_subplot(212)
        self.canvas_auto = FigureCanvas(self.figure_stat)
        self.toolbar_auto = NavigationToolbar(self.canvas_auto, self)
        self.toolbar.resize(1, 10)
        self.layout_auto_figure.addWidget(self.toolbar_auto)
        self.layout_auto_figure.addWidget(self.canvas_auto)
        self.figure_stat.tight_layout()
        self.canvas_auto.draw()

    def parse_data(self, dataset):
        #filename = QtWidgets.QFileDialog.getOpenFileName(directory='/nsls2/xf08id/Sandbox',
                                                        # filter='*.xas', parent=self)[0]
        #print(filename)
        # if filename[-4:] == '.dat':
        #     filename = filename[:-4]

        self.dataset = dataset

        for name, included in zip(dataset.name_list, dataset.is_included_list):
            item = QListWidgetItem(name)
            # item.setDropEnabled(False)
            item.setCheckState(int(included)*2)
            # item.setEditable(False)
            self.listWidget_data.addItem(item)
        self.display_data()

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

    def findclosest(self, lst, K):
        closest = lst[min(range(len(lst)), key=lambda i: abs(lst[i] - K))]
        print (closest)
        return closest

    def validate_parameters(self):
        cols_text = self.columnsText.toPlainText()
        components_text = self.componentsText.toPlainText()
        energy_text = self.energyText.toPlainText()
        svdauto_text = self.svd_auto_limits.toPlainText()
        singval_text = self.svd_sing_limits.toPlainText()
        offsetD = self.dataOffsetWhole.toPlainText()
        if offsetD == "":
            offsetD = 0
        else:
            offsetD = int(offsetD)

        if components_text == "":
            components = 3
        elif components_text != "":
            if int(components_text) <= 0:
                QMessageBox.about(self, "ERROR", "The number of components is too low. Retry.")
            else:
                components = int(components_text)

        n_cmp_show = components

        # tempSet = copy.deepcopy((self.dataset))
        if svdauto_text != "":
            n_val_show = int(svdauto_text)
        else:
            n_val_show = 25

        if energy_text == "":
            pass
        elif energy_text != "":
            energy_text = energy_text.split(",")
            e_lo = int(energy_text[0])
            e_hi = int(energy_text[1])
            if e_lo < self.dataset._x.min() or e_hi > self.dataset._x.max():
                QMessageBox.about(self, "ERROR", "The energy range is invalid. Displaying default range.")
                # tempSet = tempSet
            else:
                self.dataset.set_x_limits(e_lo, e_hi)
                # i, firstRow = self.getFirstLimit(int(energy_text[0]), tempSet._x)
                # secondRow = self.getSecondLimit(int(energy_text[1]), tempSet._x, i)
                # print("First Row: " + str(firstRow))
                # print("Second Row: " + str(secondRow))
                # tempSet._data = tempSet._data[firstRow:secondRow, 1:]
                # #tempSet._x = np.array(tempSet._x)
                # tempSet._x = tempSet._x[firstRow:secondRow]
                #x = np.array(x)
                #print(self.dataset[:,0])


        return offsetD, n_cmp_show, n_val_show#, tempSet

    def display_data(self):

        self.figure_data.ax.clear()
        self.figure_data.ax2.clear()
        self.figure_svd.clear()
        self.figure_stat.clear()

        self.dataset.plot_data(ax=self.figure_data.ax)

        offsetD, n_cmp_show, n_val_show = self.validate_parameters()


        # self.figure_svd.clear()

        # n_val_show = n_val_show
        # n_cmp_show = n_cmp_show
        # self.dataset = tempSet
        self.dataset.plot_svd(self.figure_svd, self.figure_stat, n_cmp_show=n_cmp_show, n_val_show=n_val_show)

        # self.figure_data.ax.title.set_text("Data")
        # self.figure_data.ax.set_xlabel("Energy(eV)")
        # self.figure_data.ax.set_ylabel("Mu Normalized")

        #
        # self.figure_data.ax2.title.set_text("Data Cuts")
        # self.figure_data.ax2.set_xlabel("Curve Index")
        # self.figure_data.ax2.set_ylabel("Mu Normalized")
        #
        #
        # self.figure_svd.ax.title.set_text("Subset of U")
        #
        # self.figure_svd.ax2.title.set_text("Subset of V")
        # self.figure_svd.ax2.legend()
        #
        # self.figure_stat.ax3.title.set_text("Significance Testing")#sing
        # self.figure_stat.ax3.set_xlabel("Component Index")
        # self.figure_stat.ax3.set_ylabel("Singular Values")
        #
        # self.figure_stat.ax4.title.set_text("Significance Testing") #auto
        # self.figure_stat.ax4.set_xlabel("Component Index")
        # self.figure_stat.ax4.set_ylabel("Autocorrelation")

        self.figure_data.tight_layout()
        self.figure_svd.tight_layout()
        self.figure_stat.tight_layout()

        self.canvas.draw_idle()
        self.canvas_data.draw_idle()
        self.canvas_auto.draw_idle()


    def sort_data_by(self):
        if self.dataset is not None:
            energy = self.dataset._x
            if(self.mouseCoords[0] <= energy.max() and self.mouseCoords[0] >= energy.min()):
                num = self.findclosest(energy, self.mouseCoords[0])
                i = np.where(energy == num)[0][0]

                idx_order = np.argsort(self.dataset._data[i, :]).squeeze()

                self.dataset._data = self.dataset._data[:, idx_order]
                for key in self.dataset.t_dict.keys():
                    this_list = self.dataset.t_dict[key]
                    self.dataset.t_dict[key] = [this_list[k] for k in idx_order]
                        # self.dataset.t_dict[key][idx_order]
                self.dataset.t_dict['index'] = list(range(len(self.dataset.t_dict['index'])))
                self.dataset.set_t('index')

