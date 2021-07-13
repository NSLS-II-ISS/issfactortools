import re
import sys
import numpy as np
import pkg_resources
import math

from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtCore import QThread, QSettings

from .widgets import widget_data_overview

ui_path = pkg_resources.resource_filename('issfactortools', 'ui/ui_main.ui')



class FactorAnalysisGUI(*uic.loadUiType(ui_path)):

    progress_sig = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.abc = 1
        self.widget_data_overview = widget_data_overview.UIDataOverview()
        self.layout_data_overview.addWidget(self.widget_data_overview)


if __name__ == '__main__':
    factor_gui = FactorAnalysisGUI()
    factor_gui.show()
