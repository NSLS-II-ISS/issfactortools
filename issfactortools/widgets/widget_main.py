import re
import sys
import numpy as np
import pkg_resources
import math

from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtCore import QThread, QSettings

from issfactortools.widgets import widget_data_overview

ui_path = pkg_resources.resource_filename('issfactortools', 'ui/ui_main.ui')



class FactorAnalysisGUI(*uic.loadUiType(ui_path)):

    progress_sig = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.widget_data_overview = widget_data_overview.UIDataOverview()
        self.layout_data_overview.addWidget(self.widget_data_overview)




def main_show():
    xfactor_gui = FactorAnalysisGUI()
    xfactor_gui.show()
    return xfactor_gui


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QTimer
    import sys

    app = QApplication(sys.argv)
    print('before init')
    xfactor_gui = FactorAnalysisGUI()
    print('after init')

    def xfactor():
        xfactor_gui.show()

    QTimer.singleShot(1, xfactor)  # call startApp only after the GUI is ready
    sys.exit(app.exec_())

    sys.stdout = xlive_gui.emitstream_out
    sys.stderr = xlive_gui.emitstream_err

