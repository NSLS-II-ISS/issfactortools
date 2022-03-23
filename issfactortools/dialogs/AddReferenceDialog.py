from PyQt5 import uic, QtGui, QtCore
import pkg_resources

ui_path = pkg_resources.resource_filename('issfactortools', 'dialogs/AddReferenceDialog2.ui')

class AddReferenceDialog(*uic.loadUiType(ui_path)):

    def __init__(self, reference_set_name_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle('Adding the references')

        self.listWidget_reference_sets.clear()
        self.listWidget_reference_sets.addItems(reference_set_name_list)
        self.listWidget_reference_sets.itemSelectionChanged.connect(self._enable_add_to_existing_button)
        self.pushButton_add_to_existing_set.clicked.connect(self.add_to_existing_set)
        self.pushButton_add_to_new_set.clicked.connect(self.add_to_new_set)
        self.value = None

    # def _get_selected_indexes(self):
    #     return self.listWidget_reference_sets.selectedItems()

    def _enable_add_to_existing_button(self):
        selection = self.listWidget_reference_sets.selectedItems()
        if len(selection) >= 0:
            self.pushButton_add_to_existing_set.setEnabled(1)
        else:
            self.pushButton_add_to_existing_set.setEnabled(0)

    def add_to_existing_set(self):
        selection = self.listWidget_reference_sets.selectedIndexes()
        if len(selection) == 1:
            self.value = selection[0].row()
            self.done(1)

    def add_to_new_set(self):
        self.value = None
        self.done(1)

    def get_value(self):
        return self.value