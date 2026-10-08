import pytest

pytest.importorskip("PyQt5")


def test_gui_and_packaged_ui_resources():
    from PyQt5.QtWidgets import QApplication
    from issfactortools.dialogs.AddReferenceDialog import AddReferenceDialog
    from issfactortools.widgets.widget_data_overview import UIDataOverview
    from issfactortools.widgets.widget_main import FactorAnalysisGUI

    app = QApplication.instance() or QApplication([])
    widgets = [FactorAnalysisGUI(), UIDataOverview(), AddReferenceDialog(["reference"])]
    app.processEvents()
    for widget in widgets:
        widget.close()
