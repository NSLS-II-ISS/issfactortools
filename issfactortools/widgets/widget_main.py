import re
import sys
import numpy as np
import pkg_resources
import math

from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtCore import QThread, QSettings

ui_path = pkg_resources.resource_filename('issfactortools', 'ui/ui_main.ui')

class XliveGui(*uic.loadUiType(ui_path)):

    progress_sig = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.abc = 1

